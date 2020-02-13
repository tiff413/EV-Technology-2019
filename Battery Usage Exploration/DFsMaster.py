#===============================================================================
# CONTAINS ALL EXISTING DFs AND FUNCTIONS
#===============================================================================

# 1.IMPORT MODULES

import datetime as dt
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

#===============================================================================
# 2.DEFINE FUNCTIONS

# CONVERT TIME VALUES TO A COMPARABLE FORMAT
def readTime(ti):                                               # readTime has one input, i
    a = dt.datetime.strptime(ti, "%Y-%m-%d %H:%M:%S")               # Use strptime on input i
    return a                                                        # Return strpped input

#===============================================================================
# 3.EXTRACT AND PROCESS DATA FROM CSV FILES
#   * Produce the following data frames:
#     "tripData" contains data about trip times and start/end charge.
#     "EVData" contains data about battery percentage during the trip.
#
#   * Rename vrn12 to vrn3, since vrn3 has no battery data.

# READ TRIP SUMMARY DATA, REFER TO AS "tripData"
#   This includes: trip id, start time, end time, vrn id, start charge,
#                  end charge, charge status
df = pd.read_csv('data/190701_dongle/ev_trip_summary.csv',                      # Read trip summary csv file
                 usecols=[0,1,2,5,13,14,19,20,29])
tripData = df.loc[df['start_charge'] > 0]                                       # Only take battery charges > 0

# RENAME VRN 12 TO VRN 3 IN tripData
tripData.loc[(tripData['vrn_id'] == 12), 'vrn_id'] = 3

# REMOVE TRIP ID 882, SINCE IT IS AN ANOMALY
tripData.drop(tripData[tripData['trip_sum_id'] == 882].index, inplace=True)

# REMOVE TRIPS WHERE THE START CHARGE = END CHARGE
tripData.drop(tripData[tripData['start_charge'] == tripData['end_charge']].index, inplace=True)


# READ PID DATA, REFER TO AS "batteryData"
#   * This includes: data id, battery percentage
df2 = pd.read_csv('data/190701_dongle/ev_pid.csv', usecols=[1,4])               # Read EV pid csv file
batteryData = df2.loc[df2['pid_batt_perc'] > 0]                                 # Only take battery charges > 0

# READ IN EV DATA, REFER TO AS "EVData"
#   * This includes: data id, vrn id, date time
df3 = pd.read_csv('data/190701_dongle/ev_data.csv', usecols=[0,3,23])           # Read EV data csv file
unsortedEVData = df3.loc[df3['payload_recorded_at'] != '0000-00-00 00:00:00']   # Get rid of invalid date time entries

# MERGE EV DATA AND PID DATA
mergedEVData = pd.merge(unsortedEVData, batteryData,                            # Merge by 'data_id'
                        how='inner', on=['data_id'])

# SORT MERGED EV DATA BY VRN ID AND DATA ID, REFER TO AS "EVData"
#   * This includes: data id, vrn id, date time, battery percentage
dupEV = mergedEVData.sort_values(by=['vrn_id', 'payload_recorded_at'])          # Sort by 'vrn_id' then 'payload_recorded_at'

# REMOVE DUPLICATES
EVData = dupEV.drop_duplicates(subset='payload_recorded_at',                    # Keep the one with lower 'data_id'
                               keep='first')

# RENAME VRN12 TO VRN3
EVData.loc[EVData['vrn_id']==12, 'vrn_id'] = 3

#===============================================================================
# 4.SPLIT "EVData" INTO DIFFERENT DATA FRAMES PER CAR
#   Use library system to separate data frames so that data for specific cars
#   can be searched when necessary, instead of searching the large data frame
#   "EVData" for every trip.

# CREATE AN EMPTY LIST FOR EVERY CAR
b = [1,2,3,4,5,6,7,8]                                           # Set keys as numbers from 1 to 8 representing each car
dataByVRN = {}                                                  # Set dictionary name as 'dataByVRN'
for carNum in b:                                                # For every key:
    dataByVRN['%s' % carNum] = []                                   # The value = an empty list

# CREATE SEPARATE DATA FRAMES FOR EACH CAR
for key in range(1, 9):                                         # For every key = i:
    vrnCondition = EVData.loc[EVData['vrn_id'] == key]              # Take only values with 'vrn_id' = i in EVData
    dataByVRN[str(key)] = vrnCondition                              # Assign data frame with these values into key = i

#===============================================================================
# 5.CREATE A LIST OF DATE TIMES PER CAR
#   Similar to 3, create a library for efficient searching.

# CREATE AN EMPTY LIST FOR EVERY CAR
timeListByVRN = {}                                              # Set dictionary name as 'timeListByVRN'
for carNum in b:                                                # For every key:
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
# 6.CREATE A MASTER DATA FRAME FOR EVERY TRIP ID CALLED 'tripDataByID'
#   * Similar to 3 and 4, create a library for efficient searching.
#
#   * Includes: vrn id, date time, battery percentage, data id, charge status,
#               duration, normalised battery percentage

#-------------------------------------------------------------------------------
# 6.1.CREATE THE LIBRARY OF DATA FRAMES

# RETRIEVE LIST OF TRIP IDs
tripIDColumn = tripData['trip_sum_id']                              # Select 'trip_sum_id' column in tripData
tripIDList = tripIDColumn.values.tolist()                               # Convert column into a list

# CREATE SEPARATE DATA FRAMES FOR EACH TRIP ID
tripDataByID = {}                                                   # Set dictionary name as 'tripDataByID'
for IDnum in range(0, len(tripIDList)):                             # For every Trip ID number:
    tripDataByID['%s' % tripIDList[IDnum]] = []                         # Put trip data into data frame

#-------------------------------------------------------------------------------
# 6.2.ORGANISE THE DATA FRAMES PER TRIP AND ASSIGN TO CORRECT KEY IN LIBRARY

# CONVERT tripData INTO LIST FORMAT FOR ITERATION
tripDataList = tripData.values.tolist()

# CREATE A DATA FRAME FOR EVERY TRIP ID
for i in range(0, len(tripDataList)):                               # For every trip id:
    # READ IN INFO ABOUT TRIP
    c = tripDataList[i]                                                 # Select row i
    tripID = c[0]                                                       # Extract trip id
    startT = readTime(c[1])                                             # Extract start time
    endT = readTime(c[2])                                               # Extract end time
    vrn = c[3]                                                          # Extract vrn
    startC = float(c[4])                                                # Extract start charge as a float
    endC = float(c[5])                                                  # Extract end charge as a float
    isC = float(c[8])                                                   # Extract charge status as a float

    # FIND DATE TIMES IN BETWEEN START AND END TIME
    dateTs = []                                                     # Create empty list for date times
    for j in range(0, len(timeListByVRN[str(vrn)])):                # For every date time in relevant date time list:
        if startT <= timeListByVRN[str(vrn)][j] <= endT:                # If start time <= date time <= end time:
            dateTs.append(timeListByVRN[str(vrn)][j])                       # Append date time to list

    # CONVERT DATE TIMES BACK TO STRING FOR COMPARING AND MERGING
    for k in range(0, len(dateTs)):                                 # For every time in date times list:
        d = str(dateTs[k])                                              # Convert time to string
        dateTs[k] = d                                                   # Store string in original index

    # PUT DATE TIMES INTO A DATA FRAME
    newDF = pd.DataFrame(dateTs, columns=['payload_recorded_at'])   # Name the column 'payload_recorded_at' for merging

    # MERGE TO CREATE MASTER DATA FRAME
    mergeDF = pd.merge(dataByVRN[str(vrn)], newDF,                  # Merge by 'payload_recorded_at'
                       how='inner', on=['payload_recorded_at'])

    # # CREATE ROWS FOR START AND END DATA
    # startData = {'vrn_id':[str(vrn)],                               # Add vrn
    #              'payload_recorded_at':[str(startT)],               # Add start time under 'payload_recorded_at'
    #              'pid_batt_perc':[str(startC)]}                     # Add start charge under 'pid_batt_perc'
    #
    # endData = {'vrn_id':[str(vrn)],                                 # Add vrn
    #            'payload_recorded_at':[str(endT)],                   # Add end time under 'payload_recorded_at'
    #            'pid_batt_perc':[str(endC)]}                         # Add end charge under 'pid_batt_perc'
    #
    # # CONCATENATE START AND END DATA TO MASTER DATA FRAME
    # addS = pd.concat([pd.DataFrame(startData), mergeDF],            # Read start data row as a data frame and concatenate
    #                  ignore_index=True, sort=False)
    # addE = pd.concat([addS, pd.DataFrame(endData)],                 # Read end data row as a data frame and concatenate
    #                  ignore_index=True, sort=False)

    # REMOVE DUPLICATE PERCENTAGES
    tripDupDF = mergeDF.drop_duplicates(subset='pid_batt_perc',     # Keep the one with lower 'data_id'
                                        keep='first')

    tripDF = tripDupDF.reset_index(drop=True)

    # ADD NEW COLUMN FOR CHARGE STATUS
    tripDF['is_charged'] = isC                                      # Assign charge status for every row in new column

    # ADD NEW COLUMN FOR NORMALISED BATTERY
    tripDF['normal_batt'] = np.nan                                  # Assign NaN for every row in new column (dummy value)

    for n in range(0, len(tripDF)):                                 # For every row in master data frame:
        startCNew = float(tripDF.loc[0, 'pid_batt_perc'])
        currentB = float(tripDF.loc[n, 'pid_batt_perc'])                # Select the battery percentage
        diffB = currentB - startCNew                                    # Find difference between current and start battery
        tripDF.loc[n, 'normal_batt'] = diffB                            # Assign to correct index under 'normal_batt'

    # ONLY TAKE NORMALISED BATTERY VALUES <= 0
    tripDFnBatt = tripDF.loc[tripDF['normal_batt'] <= 0]
    tripDF = tripDFnBatt.reset_index(drop=True)

    # ADD NEW COLUMN FOR DURATION
    tripDF['duration'] = np.nan                                # Assign NaN for every row in new column (dummy value)

    for m in range(0, len(tripDF)):                                 # For every row in master data frame:
        startNew = tripDF.loc[0, 'payload_recorded_at']
        startTNew = readTime(startNew)
        currentT = tripDF.loc[m,'payload_recorded_at']                  # Select the date time
        diffT = readTime(currentT) - startTNew                          # Find difference between date time and start time
        diffInSecs = diffT.total_seconds()                              # Convert difference to seconds
        tripDF.loc[m,'duration'] = diffInSecs                           # Assign to correct index under 'duration'

    # ASSIGN THIS DATAFRAME TO CORRECT KEY IN tripDataByID
    tripDataByID[str(tripID)] = tripDF

#===============================================================================
# 7.CREATE A LIST FOR TRIP DATA PER CAR
#   * For efficiently finding trips within a period
#   * Date time values (start and end times) must be comparable!

# CREATE SEPARATE DATA FRAMES FOR EACH VRN
b = [1,2,3,4,5,6,7,8]
tripListByVRN = {}                                             # Set dictionary name as 'tripListByVRN'
for carNum in range(0, len(b)):                                 # For every car number:
    tripListByVRN['%s' % carNum] = []                              # The value = an empty list

# CREATE SEPARATE DATA FRAMES FOR EACH CAR
for key in range(1, 9):                                         # For every key = i:
    trips = tripData.loc[tripData['vrn_id'] == key]                 # Take rows with vrn ID = i in tripData
    tripsList = trips.values.tolist()                               # Convert data frame into a list

    # APPLY readTime TO ALL START TIMES
    for c in range(0, len(tripsList)):                              # For every row in tripsList:
        d = readTime(tripsList[c][1])                                   # Read start time through readTime
        tripsList[c][1] = d                                             # Assign to original index in list

        e = readTime(tripsList[c][2])                                   # Read end time through readTime
        tripsList[c][2] = e                                             # Assign to original index in list

    # ASSIGN DATA FRAME INTO CORRECT KEY IN LIBRARY
    tripListByVRN[str(key)] = tripsList
