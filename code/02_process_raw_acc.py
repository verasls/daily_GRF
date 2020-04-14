import pandas as pd
import numpy as np
import time
from scipy import signal
from statistics import mean
import matplotlib.pyplot as plt


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
# Put each axis into a ndarray
aX = data.iloc[:, 0].to_numpy()
aY = data.iloc[:, 1].to_numpy()
aZ = data.iloc[:, 2].to_numpy()

# Filter acceleration signal
# Create the lowpass filter
samp_freq = 100
N = 4  # Filter order
cutoff = 20  # cut-off frequency (Hz)
fnyq = samp_freq / 2  # Nyquist frequency (half of the sampling frequency)
Wn = cutoff / fnyq  # Filter parameter

b, a = signal.butter(N, Wn, btype="low")

# Process signal
aX = signal.filtfilt(b, a, aX)
aY = signal.filtfilt(b, a, aY)
aZ = signal.filtfilt(b, a, aZ)

# Compute resultant vector
aR = np.sqrt(aX ** 2 + aY ** 2 + aZ ** 2)

# Group wear time blocks in a dictionary
blocks = {}
for i in range(0, len(info["start"])):
    key_name = "block_" + str(i + 1)
    blocks[key_name] = aR[info["start"][i]:info["end"][i]]


minute = 60 * samp_freq
n_minutes = int(len(blocks["block_1"]) / minute)
peak_indice = []
peak_height = []
for i in range(0, n_minutes):
    start = i * minute
    end = (minute * (i + 1)) - 1
    # Find peaks
    height = 3 * mean(blocks["block_1"][start:end])
    distance = 0.4 * samp_freq  # seconds * sampling frequency
    peaks, properties = signal.find_peaks(blocks["block_1"], height=height,
                                          distance=distance)
    peak_indice = np.concatenate((peak_indice, peaks))
    peak_height = np.concatenate((peak_height, properties["peak_heights"]))

# # Find peaks
# height = 2 * mean(blocks["block_1"])
# distance = 0.4 * samp_freq  # seconds * sampling frequency
# peaks, properties = signal.find_peaks(blocks["block_1"], height=height,
#                                       distance=distance)

ppm = len(properties["peak_heights"]) / info["duration"][0]
print(ppm, "peaks per minute detected")

fig = plt.figure(figsize=(15, 6))
ax1 = fig.add_subplot(1, 1, 1)
ax1.plot(blocks["block_1"])
ax1.plot(peak_indice, peak_height, "x")
plt.show()
