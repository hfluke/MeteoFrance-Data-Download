import os
from time import sleep
from datetime import datetime
import MeteoFranceRequests


def readToken():
    if ".token" in os.listdir():
        with open(".token") as file:
            token = file.readline()
        return token
    else:
        return None


def getMostRecentFile(timeRes):
    
    if len(os.listdir(f"data/{timeRes}/")) == 0:
        return {
            "dept": 1,
            "station": 0,
            "year": 0
        }
    
    else:
        folder = os.listdir(f"data/{timeRes}/")[-1]
        file = os.listdir(f"data/{timeRes}/{folder}")[-1][3:]
        
        dept = int(file[:2]) if (int(file[:3]) < 971 or int(file[:3]) > 988) else int(file[:3])
        station = int(file[:8])
        year = int(file.split("_")[1])

        return {
            "dept": dept,
            "station": station,
            "year": year
        }
    

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
        reportError(stationsList.status_code, dept)
        return False


def getStationIndex(stationJson, station):
    for i in range(len(stationJson)):
        if int(stationJson[i]["id"]) >= station:
            return i


def stationInformation(token, dept, station):
    stationInfo = MeteoFranceRequests.requestStationInformation(token, station)
    
    if stationInfo.status_code == 429:
        sleep(6)
        return stationInformation(token, dept, station)
    elif stationInfo.status_code == 200:
        return stationInfo.json()[0]
    else:
        reportError(stationInfo.status_code, dept, station)
        return False


def getYears(startDate, endDate):
    startYear = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S").year
    endYear = (
        datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S") if endDate != "" else datetime.now()
    ).year
    return (startYear, endYear)


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
        reportError(stationCmd.status_code, dept, station, year)
        return False
    

def fileCommand(token, dept, station, year, command, attemptNo=0):
    fileCmd = MeteoFranceRequests.requestFileCommand(token, command)
    
    if fileCmd.status_code == 429:
        sleep(6)
        return fileCommand(token, dept, station, year, command, attemptNo)
    elif fileCmd.status_code == 201:
        return fileCmd.content
    elif fileCmd.status_code == 204 and attemptNo < 600:
        sleep(1)
        return fileCommand(token, dept, station, year, command, attemptNo+1)
    else:
        reportError(fileCmd.status_code, dept, station, year)
        return False
    

def saveFile(fileContent, dept, station, year, timeRes):
    if timeRes == "daily":
        field = "snow"
    elif timeRes == "hourly":
        field = "wind"
    else:
        raise RuntimeError
    
    if not os.path.exists(f"data/{timeRes}/dept_{dept:02}"):
        os.makedirs(f"data/{timeRes}/dept_{dept:02}")

    with open(f'data/{timeRes}/dept_{dept:02}/FR_{station}_{year}_{field}.csv', 'wb') as f:
        f.write(fileContent)


# TODO reformat error messages
def reportError(status, dept, station="na", year="na", edgeDate="na"):
    if status == 500:
        raise ValueError("status code 500")
    else:
        with open("errors.txt", "a") as file:
            file.write(f"{status},{dept},{station},{year},{edgeDate}\n")
