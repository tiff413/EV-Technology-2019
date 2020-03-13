#===============================================================================
# VERSION 1: PLOTTING BATTERY AGAINST DATE TIME FOR A TRIP
#===============================================================================

# IMPORT MODULES
import datetime as dt
import time
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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


# READ TRIP SUMMARY DATA, REFER TO AS "tripData"
#   This includes: start time, end time, vrn id, start charge, end charge
df = pd.read_csv('data/190701_dongle/ev_trip_summary.csv', usecols=[0,1,2,5,13,14]) # Read trip summary csv file
validBattery = df['start_charge'] > 0                                               # Only take battery charges > 0
tripData = df[validBattery]                                                         # Name this new data frame "tripData"
tripData

# READ PID DATA, REFER TO AS "batteryData"
#    * This includes: data id, battery percentage, PID created time
df2 = pd.read_csv('data/190701_dongle/ev_pid.csv', usecols=[1,4])                   # Read EV pid csv file
validBattery2 = df2['pid_batt_perc'] > 0                                            # Only take battery charges > 0
batteryData = df2[validBattery2]                                                    # Name this new data frame "batteryData"

# READ IN EV DATA, REFER TO AS "unsortedEVData"
#    * This includes: data id, vrn id, date time, PID created time
df3 = pd.read_csv('data/190701_dongle/ev_data.csv', usecols=[0,3,23])               # Read EV data csv file
validTime = df3['payload_recorded_at'] != '0000-00-00 00:00:00'                     # Get rid of invalid date time entries
unsortedEVData = df3[validTime]                                                     # Name this new data frame "unsortedEVData"

# MERGE EV DATA AND PID DATA
unsortedEVDataMerged = pd.merge(unsortedEVData, batteryData, how='inner', on=['data_id'])

# SORT MERGED EV DATA BY VRN ID AND DATA ID, REFER TO AS "EVData"
EVDataDuplicates = unsortedEVDataMerged.sort_values(by=['vrn_id','payload_recorded_at'])

# REMOVE DUPLICATES
#    * This includes: data id, vrn id, datetime, PID battery percentage
EVData = EVDataDuplicates.drop_duplicates(subset='payload_recorded_at', keep='first')

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

# CREATE SEPARATE DATA FRAMES FOR EACH CAR, REFER TO AS 'dataByVRN['i']'
for key in range(1, 9):                                         # For every key = i:
    vrnCondition = EVData['vrn_id'] == key                          # Take only values with 'vrn_id' = i in EVData
    dataByVRN[str(key)] = EVData[vrnCondition]                      # Assign data frame with these values into key = i

#===============================================================================
# 4.FIND DATA POINTS

# CHOOSE TRIP BY trip_sum_id
tripID = 45                                                     # Choose a trip_sum_id
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

# CREATE A LIST OF DATE TIME VALUES FROM dataByVRN
timeColumnEV = dataByVRN[str(vrnID)]['payload_recorded_at']     # Identify the column for date time in dataByVRN
timeColumnEVList = timeColumnEV.values.tolist()                 # Read date times as a list

timeListEV = []                                                 # Create empty list for processed time values
for row in range(0, len(timeColumnEVList)):                         # For every row in time column:
    list = readTime(timeColumnEVList[row])                          # Read in time values through readTime
    timeListEV.append(list)                                         # Append values to empty list

# FIND INDECES OF DATA POINTS IN BETWEEN startTime AND endTime
# FIND INDEX OF LOWER BOUNDARY FOR DATE TIME DATA
j = 0                                                           # Start search at j = 0
while startTime > timeListEV[j]:                                # Stop search once date time value is larger than startTime
    j += 1                                                          # Search next value
startIndex = j                                                  # Store index of lower boundary

# FIND INDEX OF UPPER BOUNDARY FOR DATE TIME DATA
while endTime > timeListEV[j]:                                  # Stop search once date time value is larger than endTime
    j += 1                                                          # Search next value
endIndex = j - 1                                                # Store index of upper boundary

#===============================================================================
# 5. PLOT BATTERY PERCENTAGE AGAINST DATE TIME FOR A SINGLE TRIP

# GET X COORDINATES
times = timeListEV[startIndex:endIndex+1]                       # Identify the date times inbetween saved boundaries
allTimes = [startTime]+times+[endTime]                          # Include startTime and endTime in list
x = mdates.date2num(allTimes)                                   # Read date times as number for plotting

# GET Y COORDINATES
battPercen = dataByVRN[str(vrnID)]['pid_batt_perc']             # Identify the column for battery percentage in data by car
battPercenList = battPercen.values.tolist()                     # Read as a list
charges = battPercenList[startIndex:endIndex+1]                 # Identify battery values in between the saved boundaries
allCharges = [startCharge] + charges + [endCharge]              # Include start and end charges
y = np.array(allCharges)                                        # y values = start charge + charges + end charge

# PLOT LINE GRAPH
plt.figure(figsize=(12,8))                                      # Choose size of graph
plt.title("vrn " + str(vrnID) + ", trip sum ID " + str(tripID)) # Name graph
plt.xlabel("Date time")                                         # Name x axis
plt.ylabel("Battery percentage (%)")                            # Name y axis

plt.plot_date(x, y, 'b-')                                       # Plot x and y values, 'b-' draws line instead of scatter plot
plt.gcf().autofmt_xdate()                                       # For formatting dates

plt.show()                                                      # Show graph
#===============================================================================
# GET DURATIONS FOR TRIP TIMES
duration = []                                                   # Create an empty list for duration values
for p in range(0, len(allTimes)):                               # For all date times identified for y coordinates:
    diff = allTimes[p] - allTimes[0]                                # Subtract date time by start time to get duration
    diffInSecs = diff.total_seconds()                               # Convert to seconds for plotting
    duration.append(diffInSecs)                                     # Append duration to duration list

#===============================================================================
# PLOT BATTERY PERCENTAGE AGAINST DURATION FOR A SINGLE TRIP
fig, ax = plt.subplots(figsize=(12,8))
plt.plot(duration, y)

xfmt = mpl.ticker.FuncFormatter(lambda ms, x: time.strftime('%M:%S', time.gmtime(ms)))
ax.xaxis.set_major_formatter(xfmt)
plt.show()
