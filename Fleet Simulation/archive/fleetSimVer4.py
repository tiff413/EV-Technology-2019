import pandas as pd
import numpy as np
import datetime as dt
import time
from simFunctionsVer4 import *

# %%

# number of chunks in an hour
# e.g. 3 chunks would divide the hour into 20-min shifts
chunks = 1

import json
with open("ver4and5/scenario.txt") as f: scenarios = json.load(f)

mpkw = 4                        # SET AVERAGE MILES PER kW THAT WILL DETERMINE RATE OF BATT DECREASE
mph = 16                        # SET AVERAGE MILES PER HR COVERED
runTime = 24                    # CHOOSE RUNTIME (HRS)
car_cols = ["battPerc","inDepot","battSize","chargePt"]
cp_cols = ["maxRate","inUse"]
sim_cols = ['time','car','charge_rate','batt','event']

# ######################## PARAMETERS (4 CARS) ############################
# chargeCapacity = 12             # SET MAX AVAILABLE POWER IN CENTRE (kW/hr)
# carData = [[30, 1, 30, 0], [30, 1, 30, 1], [30, 1, 30, 2], [30, 1, 30, 3]]
# chargePtData = [[7, 1], [7, 1], [7, 1], [7, 1]]

# filename = "4_cars_work"
# filename = "4_cars_meal_delivery"
# filename = "4_cars_tourism"
# filename = "4_cars_test"
# filename = "4_cars_frequent"
# filename = "4_cars_first_shift_same"
# filename = "4_cars_second_shift_same"
# #########################################################################


######################## PARAMETERS (8 CARS) ############################
chargeCapacity = 18             # SET MAX AVAILABLE POWER IN CENTRE (kW/hr)
carData = [[30, 1, 30, 0], [30, 1, 30, 1], [30, 1, 30, 2], [30, 1, 30, 3],
           [30, 1, 30, 4], [30, 1, 30, 5], [30, 1, 30, 6], [30, 1, 30, 7]]
chargePtData = [[7, 1], [7, 1], [7, 1], [7, 1],
                [7, 1], [7, 1], [7, 1], [7, 1]]

# filename = "8_cars_work"
# filename = "8_cars_meal_delivery"
# filename = "8_cars_test"
# filename = "8_cars_frequent"
filename = "8_cars_first_shift_same"
# filename = "8_cars_second_shift_same"
#########################################################################

carShifts = scenarios[filename]['carShifts']

shiftsByCar = {}                                                # Set dictionary name as 'shiftsByCar'
for cars in range(0,len(carData)):                              # For every keys of the car:
    shiftsDF = pd.DataFrame(carShifts[cars], columns=["startShift","endShift"])
    shiftsDF = shiftsDF.sort_values(by=['startShift'])
    shiftsDF = shiftsDF.reset_index(drop=True)
    shiftsByCar['%s' % cars] = shiftsDF                             # The value = an empty list


###################
# DUMB CHARGING
###################
# depot = []
# carDataDF = pd.DataFrame.from_records(carData, columns=car_cols)
# chargePtDF = pd.DataFrame.from_records(chargePtData, columns=cp_cols)
# for car in range(0, len(carDataDF)):
#     if carDataDF.loc[car,'inDepot']: depot.append(car)
#
# rcCount = 0                     # INITIALISE A COUNTER FOR RAPID CHARGES
# time = readTime("06:00")        # CHOOSE START TIME
# simulationDF = pd.DataFrame(columns=sim_cols)
#
# for i in range(0, runTime*chunks):
#     carDataDF, time, depot, simulationDF, chargePtDF = inOutDepot(carDataDF, shiftsByCar, time, depot, simulationDF, chargePtDF)
#     carDataDF, time, rcCount, simulationDF = decreaseBatt(carDataDF, mph, mpkw, shiftsByCar, time, rcCount, simulationDF, chunks)
#     carDataDF, simulationDF, chargePtDF = dumbCharge(carDataDF, depot, chargeCapacity, time, simulationDF, chargePtDF, chunks)
#     time = incrementTime(time, chunks)
# # print("No. of rapid charges: " + str(rcCount))
# dumb_sim = dfFunction(simulationDF, chunks)
# dumbDF = styleDF(dumb_sim)
# dumbDF


# ###########################
# # SMART CHARGING LEAVETIME
# ###########################
# depot = []
# carDataDF = pd.DataFrame.from_records(carData, columns=car_cols)
# chargePtDF = pd.DataFrame.from_records(chargePtData, columns=cp_cols)
# for car in range(0, len(carDataDF)):
#     if carDataDF.loc[car,'inDepot']: depot.append(car)
#
# rcCount = 0                     # INITIALISE A COUNTER FOR RAPID CHARGES
# time = readTime("06:00")        # CHOOSE START TIME
# simulationDF = pd.DataFrame(columns=sim_cols)
#
# for i in range(0, runTime*chunks):
# #     print(str(time))
#     carDataDF, time, depot, simulationDF, chargePtDF = inOutDepot(carDataDF, shiftsByCar, time, depot, simulationDF, chargePtDF)
#     carDataDF, time, rcCount, simulationDF = decreaseBatt(carDataDF, mph, mpkw, shiftsByCar, time, rcCount, simulationDF, chunks)
#     carDataDF, simulationDF, chargePtDF = smartCharge_leavetime(carDataDF, depot, shiftsByCar, time, chargeCapacity, simulationDF, chargePtDF, chunks)
#     time = incrementTime(time, chunks)
# # print("No. of rapid charges: " + str(rcCount))
# smart_leavetime_sim = dfFunction(simulationDF, chunks)
# smart_leavetimeDF = styleDF(smart_leavetime_sim)
# smart_leavetimeDF


# ###########################
# # SMART CHARGING BATT
# ###########################
depot = []
carDataDF = pd.DataFrame.from_records(carData, columns=car_cols)
chargePtDF = pd.DataFrame.from_records(chargePtData, columns=cp_cols)
for car in range(0, len(carDataDF)):
    if carDataDF.loc[car,'inDepot']: depot.append(car)

rcCount = 0                     # INITIALISE A COUNTER FOR RAPID CHARGES
time = readTime("06:00")        # CHOOSE START TIME
simulationDF = pd.DataFrame(columns=sim_cols)

for i in range(0, runTime*chunks):
#     print(str(time))
    carDataDF, time, depot, simulationDF, chargePtDF = inOutDepot(carDataDF, shiftsByCar, time, depot, simulationDF, chargePtDF)
    carDataDF, time, rcCount, simulationDF = decreaseBatt(carDataDF, mph, mpkw, shiftsByCar, time, rcCount, simulationDF, chunks)
    carDataDF, simulationDF, chargePtDF = smartCharge_batt(carDataDF, depot, shiftsByCar, time, chargeCapacity, simulationDF, chargePtDF, chunks)
    time = incrementTime(time, chunks)
# print("No. of rapid charges: " + str(rcCount))
smart_batt_sim = dfFunction(simulationDF, chunks)
smart_battDF = styleDF(smart_batt_sim)
smart_battDF


# ###########################
# # SUPER SMART CHARGING
# ###########################
# depot = []
# carDataDF = pd.DataFrame.from_records(carData, columns=car_cols)
# chargePtDF = pd.DataFrame.from_records(chargePtData, columns=cp_cols)
# for car in range(0, len(carDataDF)):
#     if carDataDF.loc[car,'inDepot']: depot.append(car)

# rcCount = 0                     # INITIALISE A COUNTER FOR RAPID CHARGES
# time = readTime("06:00")        # CHOOSE START TIME
# simulationDF = pd.DataFrame(columns=sim_cols)

# for i in range(0, runTime*chunks):
#     carDataDF, time, depot, simulationDF, chargePtD = inOutDepot(carDataDF, shiftsByCar, time, depot, simulationDF, chargePtDF)
#     carDataDF, time, rcCount, simulationDF = decreaseBatt(carDataDF, mph, mpkw, shiftsByCar, time, rcCount, simulationDF, chunks)
#     carDataDF, simulationDF, chargePtDF = superSmartCharge(carDataDF, depot, shiftsByCar, time, chargeCapacity, simulationDF, chargePtDF, chunks)
#     time = incrementTime(time, chunks)
# # print("No. of rapid charges: " + str(rcCount))
# smart_sim = dfFunction(simulationDF, chunks)
# smartDF = styleDF(smart_sim)
# # smartDF

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
