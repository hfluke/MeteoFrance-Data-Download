import sys
from MeteoFrance import main


def printMessage():
    print('Specify whether you would like to download "snow" or "wind"')
    print('Ex. python main.py snow')


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        printMessage()
    elif sys.argv[1].lower() == "snow":
        main("daily")
    elif sys.argv[1].lower() == "wind":
        main("hourly")
    else:
        printMessage()
