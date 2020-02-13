#===============================================================================
# PLOTTING
#===============================================================================

# 1.IMPORT MODULES AND DATA FRAMES

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from DFsMaster import tripData

#===============================================================================
# 2.CREATE DATA FRAME WITH START PERCENTAGE, END PERCENTAGE AND AMOUNT CHARGED

# READ IN CHARGES, NOT JOURNEYS, FROM tripData
chargeData = tripData.loc[tripData['is_charged']==1]

# ONLY READ IN START AND END PERCENTAGES
chargesDF = chargeData[['start_charge', 'end_charge']]

# CREATE A NEW COLUMN FOR AMOUNT CHARGED
chargesDF.loc[:, 'amount_charged'] = np.nan

# CONVERT THIS DATA FRAME INTO A LIST FOR INDEXING
chargesList = chargesDF.values.tolist()

# CALCULATE AND ASSIGN DIFFERENCES
for g in range(0, (len(chargesList)-1)):                    # For every charge:
    startCI = float(chargesList[g][0])                          # Read start charge at index
    endCI = float(chargesList[g][1])                            # Read end charge at index
    diff = endCI - startCI                                      # Calculate difference
    chargesList[g][2] = diff                                    # Assign value to correct position in list

# CONVERT CHARGES LIST BACK TO DATA FRAME
diffDF = pd.DataFrame(chargesList, columns=['start_charge',
                                            'end_charge',
                                            'amount_charged'])

# ONLY SELECT ROWS WHERE AMOUNT CHARGED > 3%
chargesDF = diffDF.loc[diffDF['amount_charged'] > 0]

#===============================================================================
# 3.FIND VALUES TO PLOT FROM CHARGES DATA FRAME

# FIND VALUES FOR START PERCENTAGES
yStart = []                                                             # Create an empty list for values
for a in range(0, 10):                                                  # For all start percentages:
    b = a * 10                                                              # Create lower boundary for percentage bin
    c = b + 10                                                              # Create upper boundary for percentage bin
    chargeNum = chargesDF.loc[(chargesDF['start_charge'] > b) &             # Select values within this bin
                              (chargesDF['start_charge'] <= c)]
    chargeNumPerc = (len(chargeNum)/len(chargesDF))*100                     # Find what percentage of values are in this bin
    yStart.append(chargeNumPerc)                                            # Append percentage to list

# FIND VALUES FOR END PERCENTAGES
yEnd = []                                                               # Create an empty list for values
for d in range(0, 10):                                                  # For all end percentages:
    e = d * 10                                                              # Create lower boundary for percentage bin
    f = e + 10                                                              # Create upper boundary for percentage bin
    chargeNum = chargesDF.loc[(chargesDF['end_charge'] > e) &               # Select values within this bin
                              (chargesDF['end_charge'] <= f)]
    chargeNumPerc = (len(chargeNum)/len(chargesDF))*100                     # Find what percentage of values are in this bin
    yEnd.append(chargeNumPerc)                                              # Append percentage to list

# FIND VALUES FOR AMOUNT CHARGED
yDiff = []                                                              # Create an empty list for values
for h in range(0, 10):                                                  # For all amount charged values:
    i = h * 10                                                              # Create lower boundary for percentage bin
    j = i + 10                                                              # Create upper boundary for percentage bin
    chargeNum = chargesDF.loc[(chargesDF['amount_charged'] > i) &           # Select values within this bin
                              (chargesDF['amount_charged'] <= j)]
    chargeNumPerc = (len(chargeNum)/len(chargesDF))*100                     # Find what percentage of values are in this bin
    yDiff.append(chargeNumPerc)                                             # Append percentage to list

#===============================================================================
# 4.PLOT VALUES

# CREATE LABELS FOR DISCRETE TICKS ON X AXIS
xTicks = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
          "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]

# CONVERT VALUES TO PLOT INTO ARRAYS
x = np.arange(len(xTicks))
np.array(yStart)
np.array(yEnd)
np.array(yDiff)

# PLOT BARS!!!
fig, ax = plt.subplots(figsize=(14, 10))
ax.bar(x-0.2, yStart, width=0.2, color='y', align='center')
ax.bar(x, yEnd, width=0.2, color='m', align='center')
ax.bar(x+0.2, yDiff, width=0.2, color='c', align='center')

# LABEL AXES
plt.xticks(x, xTicks)
plt.xlabel("Battery percentage (%)", fontsize=11)
plt.ylabel("Percentage of charges recorded", fontsize=11)

# CREATE LEGEND
yPatch = mpatches.Patch(color='y', label="Battery % at start of charge")
mPatch = mpatches.Patch(color='m', label="Battery % at end of charge")
cPatch = mpatches.Patch(color='c', label="Amount charged (%)")
plt.legend(handles=[yPatch, mPatch, cPatch])

plt.show()
