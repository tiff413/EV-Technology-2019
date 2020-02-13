import pandas as pd
import numpy as np
import datetime as dt
import time
from simFunctionsVer5 import *
import json
with open("ver4and5/scenario.txt") as f: scenarios = json.load(f)

chunks = getChunks()
startTime = readTime("06:00")   # CHOOSE STARTTIME
runTime = 24                    # CHOOSE RUNTIME (HRS)
mpkw = 4                        # SET AVERAGE MILES PER kW THAT WILL DETERMINE RATE OF BATT DECREASE
mph = 16                        # SET AVERAGE MILES PER HR COVERED
car_cols = ["battPerc","inDepot","battSize","chargePt"]
cp_cols = ["maxRate","inUse"]
sim_cols = ['time','car','charge_rate','batt','event']

filename = "8_cars_work"
carShifts = scenarios[filename]['carShifts']

# ######################## PARAMETERS (4 CARS) ############################
# chargeCapacity = 12             # SET MAX AVAILABLE POWER IN CENTRE (kW/hr)
# carData = [[30, 1, 30, 0], [30, 1, 30, 1], [30, 1, 30, 2], [30, 1, 30, 3]]
# chargePtData = [[7, 1], [7, 1], [7, 1], [7, 1]]

######################## PARAMETERS (8 CARS) ############################
chargeCapacity = 18             # SET MAX AVAILABLE POWER IN CENTRE (kW/hr)
carData = [[30, 1, 30, 0], [30, 1, 30, 1], [30, 1, 30, 2], [30, 1, 30, 3],
           [30, 1, 30, 4], [30, 1, 30, 5], [30, 1, 30, 6], [30, 1, 30, 7]]
chargePtData = [[7, 1], [7, 1], [7, 1], [7, 1],
                [7, 1], [7, 1], [7, 1], [7, 1]]


dumbDF, dumb_sim = runSimulation(
                        startTime, runTime,
                        carData, car_cols, carShifts,
                        chargePtData, cp_cols, chargeCapacity,
                        sim_cols, mph, mpkw, 'dumbCharge')

# smart_leavetimeDF, smart_leavetime_sim = runSimulation(
#                         startTime, runTime,
#                         carData, car_cols, carShifts,
#                         chargePtData, cp_cols, chargeCapacity,
#                         sim_cols, mph, mpkw, 'smartCharge_leavetime')
#
# smart_battDF, smart_batt_sim = runSimulation(
#                         startTime, runTime,
#                         carData, car_cols, carShifts,
#                         chargePtData, cp_cols, chargeCapacity,
#                         sim_cols, mph, mpkw, 'smartCharge_batt')
#
# smartDF, smart_sim = runSimulation(
#                         startTime, runTime,
#                         carData, car_cols, carShifts,
#                         chargePtData, cp_cols, chargeCapacity,
#                         sim_cols, mph, mpkw, 'superSmartCharge')


# ###############################################################
# # SAVE TO EXCEL (ONLY RUN WHEN ALL ALGORITHMS ARE UNCOMMENTED)
# # NOTE: CREATE A FOLDER CALLED 'TEST' FIRST
# ###############################################################
# # open writer
# writer = pd.ExcelWriter("scenario/" + filename + ".xlsx")
# # write files
# dumbDF.to_excel(
#     writer, sheet_name="dumb")
# smart_leavetimeDF.to_excel(
#     writer, sheet_name="smart_leavetime")
# smart_battDF.to_excel(
#     writer, sheet_name="smart_batt")
# smartDF.to_excel(
#     writer, sheet_name="superSmart")
# # close writer
# writer.save()

# smart_sim[['event','batt']].to_excel('output.xlsx')
