import pandas as pd
import numpy as np
from scipy import signal


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
    info["start"].append(log.iloc[i, 7] - 1)
    info["end"].append(log.iloc[i, 8] - 1)

# Read raw data file
print("Reading raw data")
data = pd.read_csv(raw_path)
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
print("Filtering acceleration")
aX = signal.filtfilt(b, a, aX)
aY = signal.filtfilt(b, a, aY)
aZ = signal.filtfilt(b, a, aZ)

# Compute resultant vector
aR = np.sqrt(aX ** 2 + aY ** 2 + aZ ** 2)

# Group wear time blocks in a dictionary
print("Grouping the acceleration signal into wear time blocks")
blocks = {}
for i in range(0, len(info["start"])):
    key_name = "block_" + str(i + 1)
    blocks[key_name] = aR[info["start"][i]:info["end"][i]]

# Find peaks for all blocks
# Peaks criteria
height = 1.3
distance = 0.4 * samp_freq  # seconds * sampling frequency
# Find peaks
for i in range(0, len(blocks)):
    print("Finding peaks for block", str(i + 1))
    acc_signal = blocks[list(blocks)[i]]
    peaks, properties = signal.find_peaks(acc_signal, height=height,
                                          distance=distance)
    # Substitute the acceleration signal by the peaks magnitudes in the dict
    blocks[list(blocks)[i]] = properties["peak_heights"]
