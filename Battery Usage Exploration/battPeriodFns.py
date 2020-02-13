#===============================================================================
# PLOTTING BATTERY CHANGE WITHIN A PERIOD
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
import matplotlib.patches as patches

# IMPORT FUNCTIONS AND DATA FRAMES
from DFsMaster import readTime
from DFsMaster import tripData
from DFsMaster import tripListByVRN
from DFsMaster import timeListByVRN
from DFsMaster import dataByVRN
from DFsMaster import tripDataByID

#===============================================================================
# 2.SET CONDITIONS

def setConditions(vrn, S, E):
    # CHOOSE CAR (vrn id)
    a = vrn
    startP = readTime(S)                                    # Apply readTime

    # CHOOSE END OF PERIOD
    endP = readTime(E)                                      # Apply readTime

    return a, startP, endP

#===============================================================================
# 4.FIND TRIP IDs WITHIN THE TIME PERIOD
#   Use for indexing when indexes are trip IDs

def findTripIDs(vrn, startP, endP):
    a = vrn
    tripsP = []                                                     # Create empty list for trip IDs
    for f in range(0, len(tripListByVRN[str(a)])):                      # For all trips in tripListByVRN:
        if startP <= tripListByVRN[str(a)][f][1] <= endP:                   # If start time is in within period:
            if startP <= tripListByVRN[str(a)][f][2] <= endP:                   # If end time is within period:
                if tripListByVRN[str(a)][f][-1] == 0:                               # If trip is not a charge
                    tripsP.append(tripListByVRN[str(a)][f][0])                          # Append trip ID to list of trip IDs

    return tripsP

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

def createMasterDF(tripsP):
    # CALCULATE ADJUSTED TIME INTO A NEW COLUMN IN tripDataByID
    arbDate = dt.timedelta(0,1000)                                      # Take an arbitrary date > 0, since datetime can't be 0
    pointer = arbDate                                                   # Set pointer at arbitrary date
    for g in range(0, len(tripsP)):                                     # For all trips within period:
        h = tripsP[g]                                                       # Index over trip IDs in list

        # ADD NEW COLUMN FOR ADJUSTED TIME
        tripDataByID[str(h)]['adjusted_time'] = np.nan                  # Place nan as a dummy value for every row

        # CONTINUE IF THERE ARE VALUES IN tripDataByID
        if len(tripDataByID[str(h)]) > 0:
            # CREATE POINTER AND ADJUST VALUE
            start = readTime(tripDataByID[str(h)].iloc[0,2])                # Read in start time from tripDataByID
            adjValue = start - pointer                                      # Set adjust value as start time minus pointer

            # ADJUST EVERY DATE TIME VALUE IN TRIP
            for i in range(0, len(tripDataByID[str(h)])):                   # For all date times in trip:
                dateT = readTime(tripDataByID[str(h)].iloc[i,2])                # Read date time through readTime
                adjT = dateT - adjValue - arbDate                               # Subtract adjust value and arb date from date time
                tripDataByID[str(h)].iloc[i,-1] = adjT                          # Assign adjusted time to correct row and column

            # MOVE POINTER
            pointer = tripDataByID[str(h)].iloc[-1,-1] + arbDate            # Move pointer to last adjusted date + arbitrary date

    # CONCATENATE TRIPS WITHIN PERIOD TO FORM A MASTER DATA FRAME
    masterDF = tripDataByID[str(tripsP[0])]                             # Start masterDF with data from first trip
    for k in range(1, len(tripsP)):                                     # For all trips (excluding first) within period:
        m = tripsP[k]                                                       # Index over trip IDs in list
        concatDF = pd.concat([masterDF, tripDataByID[str(m)]],              # Concatenate trip to masterDF
                             ignore_index=True, sort=False)
        masterDF = concatDF                                             # Assign it back to the string "masterDF"

    return masterDF

#===============================================================================
# 6.CALCULATE MILES PER kW FOR EVERY TRIP

def calculateMPKW(tripsP, vrn):
    a = vrn
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

    return mpkwTrips

#===============================================================================
# 7.CALCULATE AVERAGE MILES PER kW WITHIN PERIOD

def avgMPKW(mpkwTrips):
    # FIND VALID MILES PER kW VALUES IN LIST
    mpkwValid = []                                                      # Create an empty list for valid mpkw
    for val in range(0, len(mpkwTrips)):                                # For all mpkw values in list:
        if mpkwTrips[val] > 0.0:                                            # If value > 0:
            if mpkwTrips[val] != np.inf:                                        # If value is not infinity:
                if mpkwTrips[val] != np.nan:                                        # If value is not NaN:
                    mpkwValid.append(mpkwTrips[val])                                    # Append to list of valid values

    # CALCULATE AVERAGE MILES PER kW IF THERE ARE VALID VALUES
    if len(mpkwValid) == 0:                                             # If there are no valid mpkw values:
        print("There are no valid trips in this period.")                   # Print message
        mpkwAvg = 0
    else:                                                               # If there are valid mpkw values:
        mpkwAvgRaw = sum(mpkwValid)/len(mpkwValid)                          # Avg mpkw = sum of valid values/no. of values
        mpkwAvg = np.around(mpkwAvgRaw, decimals=2)                         # Round average to 2dp

    return mpkwAvg

#===============================================================================
# 8.FIND X AND Y COORDINATES
#   * x = adjusted time
#   * y = battery percentage

def findXY(masterDF):
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

    return x, y

#===============================================================================
# 9.FIND COORDINATES OF NODES
#   Use nodes on graph to see the start and end of individual trips.
#   Plot nodes at:
#       * 00:00:00 adjusted time
#       * The end of a every trip
#
# There may be multiple nodes for the same adjusted time. We must append
# coordinates for these unique nodes in the correct order.

def findNodesXY(tripsP, masterDF):
    # FIND THE X COORDINATE (ADJUSTED TIME) FOR THE END OF EVERY TRIP
    nodesAT = [dt.timedelta(0)]                                         # Create a list of adj times with 0 as the first entry
    for u in range(0, len(tripsP)):                                     # For all trips within period:
        v = tripsP[u]                                                       # Index over trip IDs in list
        w = tripDataByID[str(v)]                                            # Read row in tripDataByID

        # FIND ADJUSTED TIME USING END TIME OF TRIP
        if len(w) > 0:
            endT = w.loc[len(w)-1, 'payload_recorded_at']                   # Read end time of trip

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

    return nodesX, nodesY

#===============================================================================
# 10.PLOT!!!!!

def plot(vrn, x, y, nodesX, nodesY, mpkwP):
    # PLOT CONNECTED SCATTER POINTS AND NODES
    plt.plot(x, y)                                                          # Plot x and y values
    plt.plot(nodesX, nodesY, 'r+')                                          # Plot nodes as red points

    # # ANNOTATE AVERAGE MILES PER kW ONTO GRAPH
    # xA = x[-1] + 150
    # yA = y[-1] + 2
    # ax.text(xA, yA, str(mpkwP) + " mpkw", color='black',
    #         bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))


# %% ===========================================================================
# 11.FORMAT GRAPH

fig, ax = plt.subplots(figsize=(18,10))                                 # Set up graph and choose size of graph

plt.xlabel("Adjusted time (hr:min:sec)", fontsize=22)                   # Label x axis
plt.ylabel("Battery (%)", fontsize=22)                                  # Label y axis
ax.grid()                                                               # Show grid
xfmt = ticker.FuncFormatter(lambda ms,
                            x: time.strftime('%H:%M:%S', time.gmtime(ms))) # Format time stamps on x axis
ax.xaxis.set_major_formatter(xfmt)                                      # Apply x axis formatting

#===============================================================================
# 12.MASTER FUNCTION

def battPeriod(car, S, E):
    # CHOOSE CAR (vrn id)
    vrn = car

    # EXECUTE FUNCITONS
    a, startP, endP = setConditions(vrn, S, E)
    tripsP = findTripIDs(a, startP, endP)
    masterDF = createMasterDF(tripsP)
    mpkwTrips = calculateMPKW(tripsP, a)
    mpkwP = avgMPKW(mpkwTrips)
    x, y = findXY(masterDF)
    nodesX, nodesY = findNodesXY(tripsP, masterDF)
    plot(vrn, x, y, nodesX, nodesY, mpkwP)

    return mpkwP

#===============================================================================
# 13.PLOT MULTIPLE TRIPS USING A LOOP

car = 8
numP = 1
period = 60
ti = "2019-05-02 00:00:00"

mpkwAvgs = []
for i in range(0,numP):
    j = i * period
    daysS = dt.timedelta(j)
    timeS = daysS + dt.datetime.strptime(ti, "%Y-%m-%d %H:%M:%S")
    finalS = str(timeS)

    k = j + period
    daysE = dt.timedelta(k)
    timeE = daysE + dt.datetime.strptime(ti, "%Y-%m-%d %H:%M:%S")
    finalE = str(timeE)

    mpkwP = battPeriod(car, finalS, finalE)

    if mpkwP > 0:
        mpkwAvgs.append(mpkwP)

# PLOT AVERAGE
mpkwAvgP = np.around(sum(mpkwAvgs)/len(mpkwAvgs), decimals=2)

# ax.text(ha='center', yA, str(mpkwAvgP) + " mpkw", color='blue',
#         bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))

plt.title("Car " + str(car) + ", "
          + str(numP) + " periods from " + str(ti)
          + ", period: " + str(period) + " days",
          fontsize=22)

ax.text(0.99, 0.08, "avg: " + str(mpkwAvgP) + " mpkw",
        horizontalalignment='right',
        verticalalignment='top',
        fontsize='22', color='blue',
        bbox=dict(facecolor='none', edgecolor='blue', boxstyle='round'),
        transform=ax.transAxes)
plt.rcParams.update({'font.size': 20})                                  # Choose tick label size
plt.show()
