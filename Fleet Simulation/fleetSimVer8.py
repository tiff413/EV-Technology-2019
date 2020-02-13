import pandas as pd
import numpy as np
import datetime as dt
import time
from simFunctionsVer8 import *
# from simVisuals import *

# READ IN NECESSARY CSV FILES
filename = "shift0"
allShiftsDF = pd.read_csv("inputsVer8/schedules/" + filename + ".csv", sep=";", index_col=None)
pricesDF = pd.read_csv("inputsVer8/prices.csv", sep=";", index_col=None)
drivingDF = pd.read_csv("inputsVer8/drivingDataLowMpkw.csv", sep=";", index_col=None)
fleetData = pd.read_csv("inputsVer8/fleetData.csv", sep=";", index_col=None)

# SELECT FLEET DATA
fleetData = selectCase(fleetData, {
    'smallCars':0, 'mediumCars':4, 'largeCars':0,
    'slowChargePts':0, 'fastChargePts':4, 'rapidChargePts':0
})

print("finish importing data")

# SELECT PRICE OPTION
company = "BritishGas"

# SELECT RAPID CHARGE INFORMATION
RCduration = 30     # RAPID CHARGE DURATION (MINUTES)
RCperc = 20         # WHAT PERCENTAGE TO START RAPID CHARGING (%)

# CHOOSE START TIME AND RUN TIME (HOURS)
startTime = readTime("2019-01-01 06:00:00")
runTime = 24*5


# showDF, dumb_sim = runSimulation(startTime, runTime, RCduration, RCperc,
#                         fleetData, drivingDF, allShiftsDF, pricesDF, company,
#                         dumbCharge)
#
# print("finish dumb charging")

# showDF, smart_leavetime_sim = runSimulation(startTime, runTime, RCduration, RCperc,
#                         fleetData, drivingDF, allShiftsDF, pricesDF, company,
#                         smartCharge_leavetime)
#
# print("finish leavetime charging")

# showDF, smart_batt_sim = runSimulation(startTime, runTime, RCduration, RCperc,
#                         fleetData, drivingDF, allShiftsDF, pricesDF, company,
#                         smartCharge_batt)
#
# print("finish battleft charging")

# showDF, smart_sim = runSimulation(startTime, runTime, RCduration, RCperc,
#                         fleetData, drivingDF, allShiftsDF, pricesDF, company,
#                         smartCharge_battOverLeavetime)
#
# print("finish priority charging")

showDF, cost_sim = runSimulation(startTime, runTime, RCduration, RCperc,
                        fleetData, drivingDF, allShiftsDF, pricesDF, company,
                        costSensitiveCharge)

print("finish priority charging")

# total_cars = 4
# total_algos = 4

# compareCars(filename, dumb_sim, 'dumb', total_cars)
# compareCars(filename, smart_leavetime_sim, 'leavetime', total_cars)
# compareCars(filename, smart_batt_sim, 'batt', total_cars)
# compareCars(filename, smart_sim, 'smart', total_cars)

# for car in range(total_cars):
#     result = pd.concat([getCarDF(dumb_sim, 'dumb', car),
#                         getCarDF(smart_leavetime_sim, 'leavetime', car),
#                         getCarDF(smart_batt_sim, 'batt', car),
#                         getCarDF(smart_sim, 'smart', car)])
#     compareAlgo(filename, result, car, total_algos)

# print("complete")

showDF
