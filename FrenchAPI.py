import os
from time import sleep
from datetime import datetime

import MeteoFranceUtil
import MeteoFranceRequests

DEPARTMENT_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 
    57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
    75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92,
    93, 94, 95,  971, 972, 973, 974, 975, 984, 985, 986, 987, 988, 99
]


def downloadData(timeRes):

    token = MeteoFranceUtil.readToken()

    mostRecent = MeteoFranceUtil.getMostRecentFile(timeRes)
    deptIdx = DEPARTMENT_NUMBERS.index(mostRecent["dept"])
    for dept in DEPARTMENT_NUMBERS[deptIdx:]:

        stationJson = listStations(token, dept, timeRes)
        if not stationJson:
            continue

        stationIdx = MeteoFranceUtil.getStationIndex(stationJson, mostRecent["station"]) if dept == mostRecent["dept"] else 0
        for s in stationJson[stationIdx:]:
            station = s["id"]

            stationInfoJson = stationInformation(token, dept, station)
            if not stationInfoJson:
                continue

            startYear, endYear = MeteoFranceUtil.getYears(stationInfoJson["dateDebut"], stationInfoJson["dateFin"])
            years = range(startYear, endYear+1)
            yearIdx = years.index(mostRecent["year"]) if int(station) == mostRecent["station"] else 0

            for year in years[yearIdx:]:
                
                command = stationCommand(token, dept, station, year, timeRes)
                if not command:
                    continue
                    
                commandContent = fileCommand(token, dept, station, year, command)
                if not commandContent:
                    continue

                saveFile(commandContent, dept, station, year, timeRes)
                        

def listStations(token, dept, timeRes):
    if timeRes == "daily":
        stationsList = MeteoFranceRequests.requestStationsList(token, dept, "precipitation", "quotidienne")
    elif timeRes == "hourly":
        stationsList = MeteoFranceRequests.requestStationsList(token, dept, "vent", "horaire")
    else:
        raise RuntimeError
    

    if stationsList.status_code == 429:
        sleep(6)
        return listStations(token, dept, timeRes)
    elif stationsList.status_code == 200:
        return stationsList.json()
    else:
        MeteoFranceUtil.reportError(stationsList.status_code, dept)
        return False


def stationInformation(token, dept, station):
    stationInfo = MeteoFranceRequests.requestStationInformation(token, station)
    
    if stationInfo.status_code == 429:
        sleep(6)
        return stationInformation(token, dept, station)
    elif stationInfo.status_code == 200:
        return stationInfo.json()[0]
    else:
        MeteoFranceUtil.reportError(stationInfo.status_code, dept, station)
        return False


def stationCommand(token, dept, station, year, timeRes):
    if timeRes == "daily":
        stationCmd = MeteoFranceRequests.requestStationCommand(token, station, year, "quotidienne")
    elif timeRes == "hourly":
        stationCmd = MeteoFranceRequests.requestStationCommand(token, station, year, "horaire")
    else:
        raise RuntimeError
    
    if stationCmd.status_code == 429:
        sleep(6)
        return stationCommand(token, dept, station, year, timeRes)
    elif stationCmd.status_code == 202:
        return stationCmd.json()["elaboreProduitAvecDemandeResponse"]["return"]
    else: 
        MeteoFranceUtil.reportError(stationCmd.status_code, dept, station, year)
        return False


def fileCommand(token, dept, station, year, command, attemptNo=0):
    fileCmd = MeteoFranceRequests.requestFileCommand(token, command)
    
    if fileCmd.status_code == 429:
        sleep(6)
        return fileCommand(token, dept, station, year, command, attemptNo)
    elif fileCmd.status_code == 201:
        return fileCmd.content
    elif fileCmd.status_code == 204 and attemptNo < 600:
        # sleep(0.1)
        sleep(1)
        return fileCommand(token, dept, station, year, command, attemptNo+1)
    else:
        MeteoFranceUtil.reportError(fileCmd.status_code, dept, station, year)
        return False
    

def saveFile(fileContent, dept, station, year, timeRes):
    if timeRes == "daily":
        field = "snow"
    elif timeRes == "hourly":
        field = "wind"
    else:
        raise RuntimeError
    
    # if not os.path.exists(f"data/{timeRes}_new/dept_{dept}"):
    #     os.makedirs(f"data/{timeRes}_new/dept_{dept}")
    if not os.path.exists(f"data/{timeRes}/dept_{dept:02}"):
        os.makedirs(f"data/{timeRes}/dept_{dept:02}")

    # with open(f'data/{timeRes}_new/dept_{dept}/FR_{station}_{year}_{field}.csv', 'wb') as f:
    with open(f'data/{timeRes}/dept_{dept:02}/FR_{station}_{year}_{field}.csv', 'wb') as f:
        f.write(fileContent)


def main(timeRes):
    while True:
        try:
            downloadData(timeRes)
            break
        except RuntimeError as e:
            print(f"Base exception at {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")} : {e}")
            break
        except Exception as e:
            print(f"Error at {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")} : {e}")
            sleep(60)
            continue
