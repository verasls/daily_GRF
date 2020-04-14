import pandas as pd
import numpy as np
import time


# Get path to data
data_dir = "/Volumes/LVERAS/data/"
log_path = data_dir + "wear_time/068.csv"
raw_path = data_dir + "068_4th_raw.txt"

# Read wear time log
log = pd.read_csv(log_path)

# Get info from log
info = {"duration": [], "week_day": [], "start": [], "end": []}
for i in range(0, len(log.index)):
    info["duration"].append(log.iloc[i, 6])
    info["week_day"].append(str(log.iloc[i, 3])[:3])
    info["start"].append(log.iloc[0, 7] - 1)
    info["end"].append(log.iloc[0, 8] - 1)

# Read raw data file
start_time = time.time()
data = pd.read_csv(raw_path)
print("pd.read_csv took %s seconds" % (time.time() - start_time))
# Put each axis into a ndarray and get resultant vector
aX = data.iloc[:, 0].to_numpy()
aY = data.iloc[:, 1].to_numpy()
aZ = data.iloc[:, 2].to_numpy()
aR = np.sqrt(aX ** 2 + aY ** 2 + aZ ** 2)

# Group wear time blocks in a dictionary
blocks = {}
for i in range(0, len(info["start"])):
    key_name = "block_" + str(i + 1)
    blocks[key_name] = aR[info["start"][i]:info["end"][i]]
