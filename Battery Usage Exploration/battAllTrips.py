#===============================================================================
# PLOTTING BATTERY CHANGE AGAINST DURATION FOR ALL TRIPS PER CAR
#===============================================================================

# 1.IMPORT MODULES
import datetime as dt
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from DFsMaster import readTime
from DFsMaster import tripData
from DFsMaster import tripDataByID
from DFsMaster import timeListByVRN
from DFsMaster import dataByVRN

# %% ===========================================================================
# 1.LETS PLOT!!!!!!!!!! PLOT BATTERY CHANGE AGAINST DURATION FOR ONE TRIP

# CHOOSE A TRIP ID, p
p = 45

# FIND X AND Y VALUES FROM tripDataByID
plotTripData = tripDataByID[str(p)][['normal_batt','duration']]         # Select columns 'normal_batt' and 'duration'
x = plotTripData['duration'].values.tolist()                            # x values = list of 'duration' values
y = plotTripData['normal_batt'].values.tolist()                         # y values = list of 'normal_batt' values

# PLOT
fig, ax = plt.subplots(figsize=(18,10))                                 # Set up graph and choose size of graph
plt.plot(x, y)                                                          # Plot x and y values

# FORMAT GRAPH
fig.suptitle("Trip " + str(p), fontsize=13)                             # Label title of graph
plt.xlabel("duration (min:sec)", fontsize=11)                           # Label x axis
plt.ylabel("battery decrease (%)", fontsize=11)                         # Label y axis
ax.grid()                                                               # Show grid
xfmt = ticker.FuncFormatter(lambda ms,                                  # Format time stamps on x axis
                            x: time.strftime('%M:%S', time.gmtime(ms)))
ax.xaxis.set_major_formatter(xfmt)                                      # Apply x axis formatting

plt.show()


# %% ===========================================================================
# 2.PLOT BATTERY CHANGE AGAINST DURATION FOR ALL TRIPS PER CAR

# CHOOSE A CAR, q
q = 8

# RETRIEVE A LIST OF TRIP IDs TO PLOT
trips = tripData.loc[(tripData['vrn_id'] == q)                                  # Only plot trips (not charges) of car q
                     & (tripData['is_charged'] == 0)]
tripsFinal = trips.loc[trips['start_charge'] > trips['end_charge']]             # Only trips where start charge > end charge
tripIDByVRN = tripsFinal['trip_sum_id']                                         # Select the column with trip IDs
tripIDList = tripIDByVRN.values.tolist()                                        # Convert this column into a list

# PLOT MULTIPLE TRIPS ONTO ONE GRAPH
fig, ax = plt.subplots(figsize=(18,10))                                         # Set up graph and choose size of graph
tripCount1 = 0                                                                  # Set up trip counter
for r in range(0, len(tripIDList)):                                             # For every trip in the list:
    ID = tripIDList[r]                                                              # Retrieve trip ID
    plotTripData2 = tripDataByID[str(ID)][['normal_batt','duration']]               # Select 'normal_batt' and 'duration'
    x = plotTripData2['duration'].values.tolist()                                   # x values = list of 'duration' values
    y = plotTripData2['normal_batt'].values.tolist()                                # y values = list of 'normal_batt' values
    tripCount1 += 1                                                                 # +1 to the trip counter

    ax.plot(x, y)                                                                   # Plot x and y values

# FORMAT GRAPH
ax.set_title("Car " + str(q) + ", all " + str(tripCount1) + " trips",               # Label title of graph
             fontsize=22)
plt.rcParams.update({'font.size': 20})                                              # Choose size of ticks
plt.xlabel("duration (min:sec)", fontsize=22)                                       # Label x axis
plt.ylabel("battery change (%)", fontsize=22)                                       # Label y axis
xfmt = ticker.FuncFormatter(lambda ms,
                            x: time.strftime('%M:%S', time.gmtime(ms)))             # Format time stamps on x axis
ax.xaxis.set_major_formatter(xfmt)                                                  # Apply x axis formatting

plt.show()

# %% ===========================================================================
# 3.PLOT BATTERY CHANGE AGAINST DURATION FOR ALL TRIPS PER CAR
#                   !!!BUT WITH CONDITIONS!!!
#
#   Set the following conditions:
#     * total trip duration > chosen value
#     * total change in battery < 0 (some battery has to be used)

# CHOOSE A CAR
s = 6

# CHOOSE MIN DURATION (seconds)
minD = 1200

# CHOOSE MIN CHANGE IN BATTERY (%)
minB = 0

# RETRIEVE A LIST OF TRIP IDs TO PLOT
tripDataByVRN = tripData.loc[(tripData['vrn_id'] == s)                      # Only plot trips (not charges) of car s
                             & (tripData['is_charged']==0)]
tripIDByVRN = tripDataByVRN['trip_sum_id']                                  # Select the column with trip IDs
tripIDList = tripIDByVRN.values.tolist()                                    # Make this column into a list

# PLOT MULTIPLE TRIPS ONTO ONE GRAPH
tripCount2 = 0                                                              # Set up trip counter
fig, ax = plt.subplots(figsize=(18,10))                                     # Set up graph and choose size of graph
for t in range(0, len(tripIDList)):                                         # For every trip in the list:
    ID = tripIDList[t]                                                      # Retrieve trip ID

    # SET CONDITIONS FOR MIN DURATION AND MIN CHANGE IN BATTERY
    last = len(tripDataByID[str(ID)])-1                                         # Find last row index
    totalDur = tripDataByID[str(ID)].loc[last,'duration']                       # Find total duration of trip using last index
    normBatt = tripDataByID[str(ID)].loc[last,'normal_batt']                    # Find total batt change using last index

    if (totalDur >= minD) and (normBatt < -minB):                               # If conditions apply:
        plotTripData2 = tripDataByID[str(ID)][['normal_batt','duration']]           # Retrieve 'normal_batt' and 'duration'
        x = plotTripData2['duration'].values.tolist()                               # x values = 'duration'
        y = plotTripData2['normal_batt'].values.tolist()                            # y values = 'normal_batt'

        ax.plot(x, y)                                                               # Plot x and y values
        tripCount2 += 1                                                             # +1 to the trip counter
    else:
        continue

# FORMAT GAPH
ax.set_title("Car " + str(s) + ", " + str(tripCount2) + ' trips, '          # Label title of graph
             + "min duration: " + str(minD) + " secs, "
             + "min battery change: " + str(minB) + "%",
             fontsize=13)
plt.xlabel("duration (min:sec)", fontsize=11)                               # Label x axis
plt.ylabel("battery change (%)", fontsize=11)                               # Label y axis
xfmt = ticker.FuncFormatter(lambda ms,                                      # Format time stamps on x axis
                            x: time.strftime('%M:%S', time.gmtime(ms)))
ax.xaxis.set_major_formatter(xfmt)                                          # Apply x axis formatting

# ax.set_xlim([0,300])                                                        # Set x axis limits
# ax.set_ylim([-3,0])                                                         # Set y axis limits

plt.show()
