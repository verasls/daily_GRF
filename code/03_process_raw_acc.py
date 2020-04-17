import glob
import os
import pickle
import pandas as pd
import numpy as np
from scipy import signal


# Getting paths
# General
data_dir = "/Volumes/LVERAS/daily_GRF/data/"
output_dir = "/Volumes/LVERAS/daily_GRF/output/"

# Specific
log_data = output_dir + "02_wear_time_logs/"
raw_data = output_dir + "01_raw_acc_data/"

log_output = output_dir + "03_wear_time_info/"
raw_output = output_dir + "04_acc_peaks/"

# Create output directory if it does not exist
if os.path.exists(log_output) is False:
    os.mkdir(log_output)
if os.path.exists(raw_output) is False:
    os.mkdir(raw_output)

# List files
log_files = sorted(glob.glob(log_data + "*.txt"))
raw_files = sorted(glob.glob(raw_data + "*.txt"))

# Process raw data
for i in range(0, len(log_files)):
    print("Processing file", i + 1, "out of", len(log_files))

    # Read wear time log
    print("Reading wear time log file:", log_files[i][-25:])
    log = pd.read_csv(log_files[i])

    # Get info from log
    info = {"duration": [], "week_day": [], "start": [], "end": []}
    for j in range(0, len(log.index)):
        info["duration"].append(log.iloc[j, 6])
        info["week_day"].append(str(log.iloc[j, 3])[:3])
        info["start"].append(log.iloc[j, 7] - 1)
        info["end"].append(log.iloc[j, 8] - 1)

    print("Writing wear time info")
    # Writing info dict in to a file
    log_output_file = log_output + log_files[i][-25:-8] + "_info.txt"
    with open(log_output_file, "wb") as handle:
        pickle.dump(info, handle)
    print("File written:", log_files[i][-25:-8] + "_info.txt")

    # Read raw data file
    print("Reading raw accelerometer data file:", raw_files[i][-15:])
    data = pd.read_csv(raw_files[i])
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
    print("Filtering acceleration signal")
    aX = signal.filtfilt(b, a, aX)
    aY = signal.filtfilt(b, a, aY)
    aZ = signal.filtfilt(b, a, aZ)

    # Compute resultant vector
    aR = np.sqrt(aX ** 2 + aY ** 2 + aZ ** 2)

    # Group wear time blocks in a dictionary
    print("Grouping the acceleration signal into wear time blocks")
    blocks = {}
    for j in range(0, len(info["start"])):
        key_name = "block_" + str(j + 1)
        blocks[key_name] = aR[info["start"][j]:info["end"][j]]

    # Find peaks for all blocks
    # Peaks criteria
    height = 1.3
    distance = 0.4 * samp_freq  # seconds * sampling frequency
    # Find peaks
    for j in range(0, len(blocks)):
        print("Finding peaks for block", str(j + 1))
        acc_signal = blocks[list(blocks)[j]]
        peaks, properties = signal.find_peaks(acc_signal, height=height,
                                              distance=distance)
        # Substitute the acceleration signal by the peaks magnitude in the dict
        blocks[list(blocks)[j]] = properties["peak_heights"]

    # Write blocks dictionary into a file
    print("Writing the acceleration peaks magnitude into a file")
    raw_output_file = raw_output + raw_files[i][-15:-8] + "_acc_peaks.txt"
    with open(raw_output_file, "wb") as handle:
        pickle.dump(blocks, handle)
    print("File written:", raw_files[i][-15:-8] + "_acc_peaks.txt")

print("Done!")
