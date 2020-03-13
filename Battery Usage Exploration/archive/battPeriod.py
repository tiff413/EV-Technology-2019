#===============================================================================
# PLOTTING BATTERY PERCENTAGES OF A CAR WITHIN A PERIOD
#===============================================================================

# 1.IMPORT

# IMPORT MODULES
import datetime as dt
import time
import pandas as pd
import numpy as np
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# IMPORT FUNCTIONS AND DATA FRAMES USING CODE FROM THE PYTHON FILE DFsMaster.py
from DFsMaster import readTime
from DFsMaster import tripData
from DFsMaster import timeListByVRN
from DFsMaster import dataByVRN
from DFsMaster import tripDataByID

#===============================================================================
# 2.SET CONDITIONS

# CHOOSE CAR (vrn id)
a = 3

# CHOOSE START OF PERIOD
dd1 = "20"                                                  # Choose date
mm1 = "06"                                                  # Choose month
YYYY1 = "2019"                                              # Choose year
HHMMSS1 = "00:00:00"                                        # Choose time

fullS = YYYY1 + "-" + mm1 + "-" + dd1 + " " + HHMMSS1       # Combine choices to form start of period
startP = readTime(fullS)                                    # Apply readTime

# CHOOSE END OF PERIOD
dd2 = "30"                                                  # Choose date
mm2 = "06"                                                  # Choose month
YYYY2 = "2019"                                              # Choose year
HHMMSS2 = "00:00:00"                                        # Choose time

fullE = YYYY2 + "-" + mm2 + "-" + dd2 + " " + HHMMSS2       # Combine choices to form end of period
endP = readTime(fullE)                                      # Apply readTime

#===============================================================================
# 3.CREATE A LIST FOR TRIP DATA PER CAR
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
tripData
tripListByVRN['6']
#===============================================================================
# 4.FIND TRIP IDs WITHIN THE TIME PERIOD
#   Use for indexing when indexes are trip IDs

tripsP = []                                                     # Create empty list for trip IDs
for f in range(0, len(tripListByVRN[str(a)])):                      # For all trips in tripListByVRN:
    if startP <= tripListByVRN[str(a)][f][1] <= endP:                   # If start time is in within period:
        if startP <= tripListByVRN[str(a)][f][2] <= endP:                   # If end time is within period:
            if tripListByVRN[str(a)][f][-1] == 0:                               # If trip is not a charge
                tripsP.append(tripListByVRN[str(a)][f][0])                          # Append trip ID to list of trip IDs

#===============================================================================
# 5.CREATE MASTER DATA FRAME FOR DATA WITHIN THIS TIME PERIOD
#   To graph all the trips on the same x axis, we must adjust date time values
#   to shift trips together as if they happened one after the other.
#
#   To do this, give every data point an "adjusted time". This value is
#   determind by:
#       * Creating a pointer at some arbitrary time (since time can't be zero).
#       * Adjust the data points of the first trip to the pointer value minus
#         the arbitrary time.
#       * Moving the pointer along the x axis to the end of the last trip plus
#         the arbitrary time.
#       * Adjust the data points of the next trip to the pointer value minus
#         the arbitrary time.
#       * Continue for all the trips within the period.

# CALCULATE ADJUSTED TIME INTO A NEW COLUMN IN tripDataByID
arbDate = dt.timedelta(0,1000)                                      # Take an arbitrary date > 0, since datetime can't be 0
pointer = arbDate                                                   # Set pointer at arbitrary date
for g in range(0, len(tripsP)):                                     # For all trips within period:
    h = tripsP[g]                                                       # Index over trip IDs in list

    # ADD NEW COLUMN FOR ADJUSTED TIME
    tripDataByID[str(h)].loc[:, 'adjusted_time'] = np.nan           # Place nan as a dummy value for every row

    # CREATE POINTER AND ADJUST VALUE
    start = readTime(tripDataByID[str(h)].iloc[0, 2])               # Read in start time from tripDataByID
    adjValue = start - pointer                                      # Set adjust value as start time minus pointer

    # ADJUST EVERY DATE TIME VALUE IN TRIP
    for i in range(0, len(tripDataByID[str(h)])):                   # For all date times in trip:
        dateT = readTime(tripDataByID[str(h)].iloc[i, 2])               # Read date time through readTime
        adjT = dateT - adjValue - arbDate                               # Subtract adjust value and arb date from date time
        tripDataByID[str(h)].iloc[i, -1] = adjT                         # Assign adjusted time to correct row and column

    # MOVE POINTER
    pointer = tripDataByID[str(h)].iloc[-1,-1] + arbDate            # Move pointer to last adjusted date + arbitrary date

# CONCATENATE TRIPS WITHIN PERIOD TO FORM A MASTER DATA FRAME
masterDF = tripDataByID[str(tripsP[0])]                             # Start masterDF with data from first trip
for k in range(1, len(tripsP)):                                     # For all trips (excluding first) within period:
    m = tripsP[k]                                                       # Index over trip IDs in list
    concatDF = pd.concat([masterDF, tripDataByID[str(m)]],              # Concatenate trip to masterDF
                         ignore_index=True, sort=False)
    masterDF = concatDF                                             # Assign it back to the string "masterDF"

#===============================================================================
# 6.CALCULATE MILES PER kW FOR EVERY TRIP

mpkwTrips = []                                                      # Create an empty list for miles per kW
for n in range(0,len(tripsP)):                                      # For all trips within period:
    p = tripsP[n]                                                       # Index over trip IDs in list

    # CALCULATE DISTANCE TRAVELLED IN MILES
    startODO = tripData.loc[p-1, 'start_odo_metres']                # Read start odometer from tripData
    endODO = tripData.loc[p-1, 'end_odo_metres']                    # Read end odometer from tripData
    dist = endODO - startODO                                        # Calculate distance by taking the difference
    distMiles = dist * 0.000621371                                  # Convert distance to miles

    # CALCULATE POWER IN kW
    #   * FIND BATTERY PERCENTAGE USED
    startC = tripData.loc[p-1, 'start_charge']                      # Read start charge from tripData
    endC = tripData.loc[p-1, 'end_charge']                          # Read end charge from tripData
    chargeDiff = startC - endC                                      # Calculate battery used by taking the difference

    #   * CALCULATE POWER ACCORDING TO CAR BATTERY
    fortykW = [1,2,3,6,8]                                           # List of cars (vrn ID) with 40kW battery
    thirtykW = [4,5,7]                                              # List of cars (vrn ID) with 30kW battery
    if fortykW.count(a) > 0:                                        # If car has a 40kW battery:
        powerKW = (chargeDiff/100)*40                                   # Power used = (batt% used/100) * 40kW
    elif thirtykW.count(a) > 0:                                     # If car has a 30kW battery:
        powerKW = (chargeDiff/100)*30                                   # Power used = (batt% used/100) * 30kW
    else:                                                           # If vrn ID isnt in fortykW or thirtykW list:
        print("car (vrn ID) doesn't exist")                             # Print message
        sys.exit()                                                      # Stop program

    # CALCULATE MILES PER kW
    mpkw = distMiles/powerKW

    # APPEND MILES PER kW TO LIST
    mpkwTrips.append(np.around(mpkw, decimals=2))

#===============================================================================
# 7.CALCULATE AVERAGE MILES PER kW WITHIN PERIOD

# FIND VALID MILES PER kW VALUES IN LIST
mpkwValid = []                                                      # Create an empty list for valid mpkw
for val in range(0, len(mpkwTrips)):                                # For all mpkw values in list:
    if mpkwTrips[val] > 0.0:                                            # If value > 0:
        if mpkwTrips[val] != np.inf:                                        # If value is not infinity:
            if mpkwTrips[val] != np.nan:                                        # If value is not NaN:
                mpkwValid.append(mpkwTrips[val])                                    # Append to list of valid values

# CALCULATE AVERAGE MILES PER kW IF THERE ARE VALID VALUES
if len(mpkwValid) == 0:                                             # If there are no valid mpkw values:
    print("There are no valid trips.")                                  # Print message
    sys.exit()                                                          # Stop program
else:                                                               # If there are valid mpkw values:
    mpkwAvgRaw = sum(mpkwValid)/len(mpkwValid)                          # Avg mpkw = sum of valid values/no. of values
    mpkwAvg = np.around(mpkwAvgRaw, decimals=2)                         # Round average to 2dp

#===============================================================================
# 8.FIND X AND Y COORDINATES
#   * x = adjusted time
#   * y = battery percentage

# FIND X VALUES FROM masterDF
times = masterDF['adjusted_time'].values.tolist()                   # Select adjusted times from masterDF
x = []                                                              # Create an empty list for x values
for q in range(0, len(times)):                                      # For all adjusted times:
    r = times[q].total_seconds()                                        # Convert adjusted time to seconds
    x.append(r)                                                         # Append adjusted tme to x values list

# FIND Y VALUES FROM masterDF
batts = masterDF['pid_batt_perc'].values.tolist()                   # Select battery percentages from masterDF
y = []                                                              # Create an empty list for y values
for s in range(0, len(batts)):                                      # For all battery percentages:
    t = float(batts[s])                                                 # Convert battery percentage to float
    y.append(t)                                                         # Append battery percentage to y values list

#===============================================================================
# 9.FIND COORDINATES OF NODES
#   Use nodes on graph to see the start and end of individual trips.
#   Plot nodes at:
#       * 00:00:00 adjusted time
#       * The end of a every trip
#
# There may be multiple nodes for the same adjusted time. We must append
# coordinates for these unique nodes in the correct order.

# FIND THE X COORDINATE (ADJUSTED TIME) FOR THE END OF EVERY TRIP
nodesAT = [dt.timedelta(0)]                                         # Create a list of adj times with 0 as the first entry
for u in range(0, len(tripsP)):                                     # For all trips within period:
    v = tripsP[u]                                                       # Index over trip IDs in list
    w = tripDataByID[str(v)]                                            # Read row in tripDataByID

    # FIND ADJUSTED TIME USING END TIME OF TRIP
    endT = w.loc[len(w)-1, 'payload_recorded_at']                       # Read end time of trip
    endAT = masterDF.loc[masterDF['payload_recorded_at'] == endT,       # Find adjusted time of end time
                         'adjusted_time'].values.tolist()

    # APPEND ADJUSTED TIME TO LIST
    nodesAT.append(endAT[0])

# FIND COORDINATES OF NODES
nodesX = []                                                         # Create an empty list for x coordinates
nodesY = []                                                         # Create an empty list for y coordinates
for z in range(0, len(nodesAT)):                                    # For all adjusted times:
    # FIND THE VALUES FOR BATTERY THAT OCCUR ON THE ADJUSTED TIME
    endB = masterDF.loc[masterDF['adjusted_time'] == nodesAT[z],        # Read these values as a list
                        'pid_batt_perc'].values.tolist()

    # CONVERT BATTERY VALUES TO FLOATS
    for aa in range(0, len(endB)):                                      # For all the battery values:
        endB[aa] = float(endB[aa])                                          # Convert battery value to floats

    # CREATE A LIST OF UNIQUE BATTERY VALUES IN ORDER
    nodeB = [endB[0]]                                                   # Start with list including first value
    for ab in range(0, len(endB)):                                      # For all battery values:
        if endB[ab] != endB[ab-1]:                                          # If the val != the last val in the list:
            nodeB.append(endB[ab])                                              # Append battery value to list

    # APPEND X AND Y COORDINATES TO LISTS IN CORRECT ORDER
    if len(nodeB) > 1:                                                  # If there is more than one battery value:
        for ac in range(0, len(nodeB)):                                     # For all battery values:
            nodesY.append(nodeB[ac])                                            # Append battery value to nodesY
            nodesX.append(nodesAT[z].total_seconds())                           # Append correlating adjusted time to nodesX

    else:                                                               # If there is only one value for battery:
        nodesY.append(nodeB[0])                                             # Append battery value to nodesY
        nodesX.append(nodesAT[z].total_seconds())                           # Append correlating adjusted time to nodesX

#===============================================================================
# 10.PLOT!!!!!

# PLOT CONNECTED SCATTER POINTS AND NODES
fig, ax = plt.subplots(figsize=(18,10))                                 # Set up graph and choose size of graph
plt.plot(x, y)                                                          # Plot x and y values
plt.plot(nodesX, nodesY, 'ro')                                          # Plot nodes as red points

# ANNOTATE MILES PER kW ONTO GRAPH
#   Annotate a point and choose where to place the text
nodeNum = 1                                                             # Start at node 1 - end of first trip
for ad in range(0, len(tripsP)):                                        # For all trips within period:
    # ANNOTATE THE NODES AT THE END OF THE TRIP
    xVal = nodesX[nodeNum]                                                  # Take the x value of the end of the trip
    yVal = nodesY[nodeNum]                                                  # Take the y value of the end of the trip

    # PLACE THE TEXT AROUND THE MIDDLE OF THE TRIP
    midT = (x.index(xVal) + x.index(nodesX[nodeNum-1])) // 2                # Find the index of the middle of trip
    xPos = x[midT] + 40                                                     # Take xPos as the middle + 40 seconds
    yPos = y[midT] + 0.2                                                    # Take yPos as the middle + 0.2% battery

    # ANNOTATE!
    ax.annotate(str(mpkwTrips[ad]) + " mpkw",                               # Annotate the mpkw for that trip
                xy=(xVal, yVal), xytext=(xPos, yPos))

    # FIND THE END OF THE NEXT TRIP
    nodeNum += 1                                                            # Search next node
    if nodeNum < (len(nodesX)-1):                                           # If nodeNum counter < number of nodes:
        while nodesX[nodeNum - 1] == nodesX[nodeNum]:                           # While nodes occur on the same adjusted time
            nodeNum += 1                                                            # Go to next node

# ANNOTATE AVERAGE MILES PER kW ONTO GRAPH
ax.text(x[0], y[0]-10, "avg: " + str(mpkwAvg) + " mpkw", color='black',
        bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))

# FORMAT GRAPH
plt.title("Car " + str(a) + ", "                                        # Label title of graph
          + str(len(tripsP)) + " trips between " + fullS
          + " and " + fullE, fontsize=13)
plt.xlabel("Adjusted time (hr:min:sec)", fontsize=11)                   # Label x axis
plt.ylabel("Battery (%)", fontsize=11)                                  # Label y axis
ax.grid()                                                               # Show grid
xfmt = ticker.FuncFormatter(lambda ms,                                  # Format time stamps on x axis
                            x: time.strftime('%H:%M:%S', time.gmtime(ms)))
ax.xaxis.set_major_formatter(xfmt)                                      # Apply x axis formatting

plt.show()
