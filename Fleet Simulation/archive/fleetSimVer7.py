import pandas as pd
import numpy as np
import datetime as dt
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from simFunctionsVer7 import *

# READ IN NECESSARY CSV FILES
allShiftsDF = pd.read_csv("ver6/4carTest.csv", sep=";", index_col=None)
pricesDF = pd.read_csv("ver7/prices.csv", sep=";", index_col=None)
drivingDF = pd.read_csv("ver7/drivingData.csv", sep=";", index_col=None)
fleetData = pd.read_csv("ver7/fleetData.csv", sep=";", index_col=None)
fleetData = selectCase(fleetData, {
    'smallCars':0, 'mediumCars':4, 'largeCars':0,
    'slowChargePts':0, 'fastChargePts':4, 'rapidChargePts':0
})

# CHOOSE START TIME AND RUN TIME
startTime = readTime("2019-01-01 06:00:00")
runTime = 24*5

# ############################
# # GENERATE A LIST OF RANDOMISED MILEAGES AND MPKW
# mpkwMean = getData(fleetData, 'mpkwMean')
# mpkwSD = getData(fleetData, 'mpkwSD')
# mileageMean = getData(fleetData, 'mileageMean')
# mileageSD = getData(fleetData, 'mileageSD')
# mileage, mpkw = generateRandomDrives(mileageMean, mpkwMean, mileageSD, mpkwSD, runTime)


# showDF, dumb_sim = runSimulation(
#                         startTime, runTime,
#                         fleetData, drivingDF, allShiftsDF, pricesDF,
#                         'dumbCharge')

showDF, smart_leavetime_sim = runSimulation(
                        startTime, runTime,
                        fleetData, drivingDF, allShiftsDF, pricesDF,
                        'smartCharge_leavetime')

# showDF, smart_batt_sim = runSimulation(
#                         startTime, runTime,
#                         fleetData, drivingDF, allShiftsDF, pricesDF,
#                         'smartCharge_batt')

# showDF, smart_sim = runSimulation(
#                         startTime, runTime,
#                         fleetData, drivingDF, allShiftsDF, pricesDF,
#                         'superSmartCharge')

showDF
