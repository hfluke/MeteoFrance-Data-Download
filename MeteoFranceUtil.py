import os
from time import sleep
from datetime import datetime


def readToken():
    if ".token" in os.listdir():
        with open(".token") as file:
            token = file.readline()
        return token
    else:
        return None


def getMostRecentFile(timeRes):
    # folder = os.listdir(f"data/{timeRes}_new/")[-1]
    # file = os.listdir(f"data/{timeRes}_new/{folder}")[-1][3:]

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


def getMostRecentFile2(timeRes):
    file = os.listdir(f"data/{timeRes}/")[-1][3:]
    
    dept = int(file[:2]) if (int(file[:2]) < 971 or int(file[:2] > 988)) else int(file[:3])
    station = int(file[:8])
    year = int(file.split("_")[1])

    return {
        "dept": dept,
        "station": station,
        "year": year
    }


def getStationIndex(stationJson, station):
    for i in range(len(stationJson)):
        if int(stationJson[i]["id"]) >= station:
            return i
        

def getYears(startDate, endDate):
    startYear = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S").year
    endYear = (
        datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S") if endDate != "" else datetime.now()
    ).year

    return (startYear, endYear)


def formatDate(year):
    return f"{year}-01-01T00:00:00Z"


def reportError(status, dept, station="na", year="na", edgeDate="na"):
    # with open("france_errors_wind.txt", "a") as file:
    #     file.write(f"{status},{dept},{station},{year},{edgeDate}\n")

    if status == 500:
        raise ValueError("status code 500")
    else:
        with open("france_errors_wind.txt", "a") as file:
            file.write(f"{status},{dept},{station},{year},{edgeDate}\n")
