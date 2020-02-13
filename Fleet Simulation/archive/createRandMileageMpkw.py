import pandas as pd
import numpy as np

from fleetSimVer7 import runTime
from simFunctionsVer7 import chunks

# GENERATE A LIST OF RANDOM VALUES FOR MILEAGE AND MPKW FOR EVERY CAR
carNum = []
mileage = []
mpkw = []

# FOR EVERY CAR
for car in range(8):

    # FOR EVERY TIME CHUNK
    for i in range(0, 24*7*3):
        # APPEND CAR INDEX
        carNum.append(car)

        # APPEND A RANDOM VALUE FOR MILEAGE
        mpkw.append(abs(np.random.normal(3.0, 1)))

        # APPEND A RANDOM VALUE FOR MPKW
        mileage.append(abs(np.random.normal(15, 2.5)))

drivingDF = pd.DataFrame(
    {'car': carNum,
     'mileage': mileage,
     'mpkw': mpkw
    }, index=None)

drivingDF.to_csv("ver6/drivingDataLowMpkwHighSD.csv", sep=';', index=False)
