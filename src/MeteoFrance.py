import os
import json
from time import sleep
from datetime import datetime
import src.MeteoFranceUtil as MeteoFranceUtil
 
DEPARTMENT_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 
    57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
    75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92,
    93, 94, 95,  971, 972, 973, 974, 975, 984, 985, 986, 987, 988, 99
]


def main(timeRes):

    if not os.path.exists(f"data"):
        os.makedirs(f"data")
    if not os.path.exists(f"data/{timeRes}"):
        os.makedirs(f"data/{timeRes}")
    if not os.path.exists(f"data/{MeteoFranceUtil.getParameter(timeRes)}_station_metadata"):
        os.makedirs(f"data/{MeteoFranceUtil.getParameter(timeRes)}_station_metadata")

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


def downloadMetadata(token, timeRes, dept):
    stationList = MeteoFranceUtil.listStations(token, dept, timeRes)
    if not stationList:
        return
    
    with open(f"data/{MeteoFranceUtil.getParameter(timeRes)}_station_metadata/dept_{dept:02}.json", "w") as f:
        json.dump(stationList, f)


def downloadData(timeRes):

    token = MeteoFranceUtil.readToken()

    mostRecent = MeteoFranceUtil.getMostRecentFile(timeRes)
    deptIdx = DEPARTMENT_NUMBERS.index(mostRecent["dept"])
    for dept in DEPARTMENT_NUMBERS[deptIdx:]:

        downloadMetadata(token, timeRes, dept)

        stationJson = MeteoFranceUtil.listStations(token, dept, timeRes)
        if not stationJson:
            continue

        stationIdx = MeteoFranceUtil.getStationIndex(stationJson, mostRecent["station"]) if dept == mostRecent["dept"] else 0
        for s in stationJson[stationIdx:]:
            station = s["id"]

            stationInfoJson = MeteoFranceUtil.stationInformation(token, dept, station)
            if not stationInfoJson:
                continue

            startYear, endYear = MeteoFranceUtil.getYears(stationInfoJson["dateDebut"], stationInfoJson["dateFin"])
            years = range(startYear, endYear+1)
            yearIdx = years.index(mostRecent["year"]) if int(station) == mostRecent["station"] else 0

            for year in years[yearIdx:]:

                command = MeteoFranceUtil.stationCommand(token, dept, station, year, timeRes)
                if not command:
                    continue
                    
                commandContent = MeteoFranceUtil.fileCommand(token, dept, station, year, command)
                if not commandContent:
                    continue

                MeteoFranceUtil.saveFile(commandContent, dept, station, year, timeRes)
   