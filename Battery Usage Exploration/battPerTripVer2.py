#===============================================================================
# VERSION 2: PLOTTING BATTERY AGAINST DATE TIME FOR A TRIP
#===============================================================================
#   Updates:
#   * Create a library for timeListByVRN
#   * Use for statements instead of while statements to find date times between
#     startTime and endTime
#   * Create a separate data frame with final processed trip data before
#     plotting
#
#===============================================================================

# IMPORT MODULES
import datetime as dt
import time
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from DFsMaster import tripData

#===============================================================================
# 1.DEFINE FUNCTIONS

# CONVERT TIME VALUES TO A COMPARABLE FORMAT
def readTime(ti):                                               # readTime has one input, i
    a = dt.datetime.strptime(ti, "%Y-%m-%d %H:%M:%S")           # Use strptime on input i
    return a                                                    # Return strpped input

#===============================================================================
# 2.EXTRACT AND PROCESS DATA FROM CSV FILES
#    * Produce the following data frames:
#       "tripData" contains data about trip times and start/end charge
#       "EVData" contains data about battery percentage during the trip
#
#    * Rename vrn12 to vrn3, since vrn3 has no battery data


# # READ TRIP SUMMARY DATA, REFER TO AS "tripData"
# #   This includes: start time, end time, vrn id, start charge, end charge
# df = pd.read_csv('data/190701_dongle/ev_trip_summary.csv',                      # Read trip summary csv file
#                  usecols=[0,1,2,5,13,14])
# validBattery = df['start_charge'] > 0                                           # Only take battery charges > 0
# tripData = df[validBattery]                                                     # Name this new data frame "tripData"


# READ PID DATA, REFER TO AS "batteryData"
#    * This includes: data id, battery percentage, PID created time
df2 = pd.read_csv('data/190701_dongle/ev_pid.csv', usecols=[1,4])               # Read EV pid csv file
validBattery2 = df2['pid_batt_perc'] > 0                                        # Only take battery charges > 0
batteryData = df2[validBattery2]                                                # Name this new data frame "batteryData"

# READ IN EV DATA, REFER TO AS "unsortedEVData"
#    * This includes: data id, vrn id, date time, PID created time
df3 = pd.read_csv('data/190701_dongle/ev_data.csv', usecols=[0,3,23])           # Read EV data csv file
validTime = df3['payload_recorded_at'] != '0000-00-00 00:00:00'                 # Get rid of invalid date time entries
unsortedEVData = df3[validTime]                                                 # Name this new data frame "unsortedEVData"

# MERGE EV DATA AND PID DATA
EVDataMerged = pd.merge(unsortedEVData, batteryData,
                                how='inner', on=['data_id'])

# SORT MERGED EV DATA BY VRN ID AND DATA ID, REFER TO AS "EVData"
EVDataDup = EVDataMerged.sort_values(by=['vrn_id','payload_recorded_at'])

# REMOVE DUPLICATES
#    * This includes: data id, vrn id, datetime, PID battery percentage
EVData = EVDataDup.drop_duplicates(subset='payload_recorded_at',
                                   keep='first')

# RENAME VRN12 TO VRN3
EVData.loc[EVData['vrn_id']==12, 'vrn_id'] = 3

#===============================================================================
# 3.SPLIT "EVData" INTO DIFFERENT DATA FRAMES PER CAR
#      Use library system to separate data frames so that data for specific cars
#      can be searched when necessary, instead of searching the large data frame
#      "EVData" for every trip.


# CREATE AN EMPTY LIST FOR EVERY CAR
x = [1,2,3,4,5,6,7,8]                                           # Set keys as numbers from 1 to 8 representing each car
dataByVRN = {}                                                  # Set dictionary name as 'dataByVRN'
for carNum in x:                                                # For every key:
    dataByVRN['%s' % carNum] = []                                   # The value = an empty list

# CREATE SEPARATE DATA FRAMES FOR EACH CAR, REFER TO AS "dataByVRN['i']"
for key in range(1, 9):                                         # For every key = i:
    vrnCondition = EVData['vrn_id'] == key                          # Take only values with 'vrn_id' = i in EVData
    dataByVRN[str(key)] = EVData[vrnCondition]                      # Assign data frame with these values into key = i

#===============================================================================
# 4.CREATE A DATE TIME LIST PER CAR

# CREATE AN EMPTY LIST FOR EVERY CAR
timeListByVRN = {}                                              # Set dictionary name as 'timeListByVRN'
for carNum in x:                                                # For every key:
    timeListByVRN['%s' % carNum] = []                               # The value = an empty list

# CREATE SEPARATE DATA FRAMES FOR EACH CAR
for key in range(1, 9):                                         # For every key = i:
    timeColumnEV = dataByVRN[str(key)]['payload_recorded_at']       # Identify the column for date time in dataByVRN
    timeColumnEVList = timeColumnEV.values.tolist()                 # Read date times as a list

    # APPLY readTime TO EACH ROW
    timeListByVRN[str(key)] = []                                    # Create empty list for processed time values
    for row in range(0, len(timeColumnEVList)):                     # For every row in time column:
        list = readTime(timeColumnEVList[row])                          # Read in time values through readTime
        timeListByVRN[str(key)].append(list)                            # Append values to empty list

#===============================================================================
# 5.FIND DATA POINTS

# CHOOSE TRIP BY trip_sum_id
tripID = 1698                                                    # Choose a trip_sum_id
i = tripID - 1                                                  # Row index is trip_sum_id - 1 (trip_sum_id starts from 1)

# RETRIEVE START CHARGE
startChargeColumn = tripData['start_charge']                    # Identify the column for start charge in tripData
startCharge = np.float(startChargeColumn[i])                    # Read in the 'i'th value as a float

# RETRIEVE END CHARGE
endChargeColumn = tripData['end_charge']                        # Identify the column for end charge in tripData
endCharge = np.float(endChargeColumn[i])                        # Read in the 'i'th value as a float

# RETRIEVE START TIME OF TRIP
startTimeColumn = tripData['start_datetime']                    # Identify the column for start time in tripData
startTime = readTime(startTimeColumn[i])                        # Read in the 'i'th value through the readTime function

# RETRIEVE END TIME OF TRIP
endTimeColumn = tripData['end_datetime']                        # Identify the column for end time in tripData
endTime = readTime(endTimeColumn[i])                            # Read in the 'i'th value through the readTime function

# RETRIEVE VRN ID OF CAR ON TRIP
vrnIDColumn = tripData['vrn_id']                                # Identify the column for vrn id in tripData
vrnID = vrnIDColumn[i]                                          # Read in the 'i'th value

# FIND DATE TIMES IN BETWEEN START AND END TIME
times = []                                                      # Create an empty list for date times
for q in range(0, len(timeListByVRN[str(vrnID)])):                  # For every date time in timeListByVRN:
    if startTime <= timeListByVRN[str(vrnID)][q] <= endTime:            # If date time is between start and end time:
        b = str(timeListByVRN[str(vrnID)][q])                           # Read date time as a string
        times.append(b)                                                 # Append date time to times list

# READ THE DATE TIMES LIST AS A DATA FRAME
newDF = pd.DataFrame(times, columns=['payload_recorded_at'])

# MERGE DATE TIMES AND dataByVRN TO FIND THE EV DATA FOR THE TRIP
mergeDF = pd.merge(dataByVRN[str(vrnID)],
                   newDF, how='inner', on=['payload_recorded_at'])

# ADD START AND END DATA TO THE MERGED DATA FRAME
#   * CREATE ROW FOR START DATA
startData = {'vrn_id':[str(vrnID)],                             # Write in vrn ID
             'payload_recorded_at':[str(startTime)],            # Write in start time as date time
             'pid_batt_perc':[str(startCharge)]}                # Write in start charge as battery percentage

#   * CREATE ROW FOR END DATA
endData = {'vrn_id':[str(vrnID)],                               # Write in vrn ID
           'payload_recorded_at':[str(endTime)],                # Write in end time as date time
           'pid_batt_perc':[str(endCharge)]}                    # Write in end charge as battery percentage

#   * CONCATENATE START DATA ROW TO MERGED DATA FRAME
addTripData = pd.concat([pd.DataFrame(startData), mergeDF],     # Read in start row as a data frame and concatenate
                        ignore_index=True, sort=False)

#   * CONCATENATE END DATA ROW TO MERGED DATA FRAME
tripDF = pd.concat([addTripData, pd.DataFrame(endData)],        # Read in end row as a dataframe and concatenate
                   ignore_index=True, sort=False)

# CREATE A NEW COLUMN FOR TRIP ID IN MERGED DATA FRAME
tripDF.loc[:,'trip_sum_id'] = tripID

#===============================================================================
# 6. PLOT BATTERY PERCENTAGE AGAINST DATE TIME FOR A SINGLE TRIP

# SELECT DATA TO PLOT FROM DATA FRAME
toPlot = tripDF[['payload_recorded_at', 'pid_batt_perc']]

# FIND X COORDINATES
#   * RUN readTime OVER EVERY DATE TIME
timesToPlot = toPlot['payload_recorded_at'].values.tolist()     # Read date times as a list
x = timesToPlot                                                 # Call this list x
for time in range(0, len(timesToPlot)):                         # For all date times:
    x[time] = readTime(timesToPlot[time])                           # Run date time through readTime

# FIND Y COORDINATES
#   * CONVERT BATTERY VALUES INTO FLOATS
battToPlot = toPlot['pid_batt_perc'].values.tolist()            # Read battery percentages as a list
y = battToPlot                                                  # Call this list y
for batt in range(0, len(battToPlot)):                          # For all battery values:
    y[batt] = float(battToPlot[batt])                               # Convert battery into a float

# PLOT!
fig, ax = plt.subplots(figsize=(14, 10))                        # Choose size of graph
ax.grid()
plt.title("vrn " + str(vrnID) + ", trip sum ID " + str(tripID)) # Name graph
plt.xlabel("Date time")                                         # Name x axis
plt.ylabel("Battery percentage (%)")                            # Name y axis

plt.plot_date(x, y, '-b')                                       # Plot x and y values, 'b-' draws line instead of scatter plot
plt.gcf().autofmt_xdate()                                       # For formatting dates

plt.show()                                                      # Show graph
