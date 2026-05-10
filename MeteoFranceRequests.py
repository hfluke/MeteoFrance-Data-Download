import requests
from MeteoFranceUtil import formatDate


# 1. Find the station identifier
def requestStationsList(token, dept, param, timeRes):
    return requests.get(
        url=f"https://public-api.meteofrance.fr/public/DPClim/v1/liste-stations/{timeRes}",
        params={
            "id-departement": dept,
            "parametre": param
        },
        headers={"apiKey": token}
    )


# 2. Retrieve station metadata
def requestStationInformation(token, station):
    return requests.get(
        url="https://public-api.meteofrance.fr/public/DPClim/v1/information-station",
        params={
            "id-station": station
        },
        headers={"apiKey": token}
    )


# 3. Ordering data
def requestStationCommand(token, station, year, timeRes):
    return requests.get(
        url=f"https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/{timeRes}",
        params={
            "id-station": station,
            "date-deb-periode": formatDate(year),
            "date-fin-periode": formatDate(year+1)
        },
        headers={"apiKey": token}
    )


# 4. Retrieve weather data from the station
def requestFileCommand(token, command):
    return requests.get(
        url="https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier",
        params={
            "id-cmde": command
        },
        headers={"apiKey": token}
    )


def formatDate(year):
    return f"{year}-01-01T00:00:00Z"
