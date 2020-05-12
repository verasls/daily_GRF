import sys
from glob import glob
import os
import pickle
import time
import pandas as pd
import numpy as np
from scipy import signal


def set_pahts(data_dir, output_dir):
    """
    Set the data and output paths

    Args:
        data_dir: A character string with the path to the data directory
        output_dir: A character string with the path to the output directory

    Returns:
        Assigns the paths to global variables
    """
    # Make variables global
    global log_data_dir
    global log_output_dir
    global log_files
    global raw_data_dir
    global raw_output_dir
    global raw_files

    # Set paths
    log_data_dir = output_dir + "part2_wear_time_logs/"
    raw_data_dir = output_dir + "part1_raw_acc_data/"

    log_output_dir = output_dir + "part3_wear_time_info/"
    raw_output_dir = output_dir + "part3_acc_peaks/"

    # Create output directory if it does not exist
    if os.path.exists(log_output_dir) is False:
        os.mkdir(log_output_dir)
    if os.path.exists(raw_output_dir) is False:
        os.mkdir(raw_output_dir)

    # List files
    log_files = [os.path.basename(x) for x in glob(log_data_dir + "*.txt")]
    raw_files = [os.path.basename(x) for x in glob(raw_data_dir + "*.txt")]
    log_files = sorted(log_files)
    raw_files = sorted(raw_files)

    # Check if there are the same number of log and raw files
    if len(log_files) == len(raw_files) is False:
        raise ValueError
        print("There is a different number of raw and log files")


def get_wear_time_info(i, ID_num, eval_num):
    """
    Reads the wear time info file, puts it into a dictionary and makes the
    dictionary global

    Args:
        i: Index of the file in the files list
        ID_num: Subject ID number
        eval_number: Subject eval number

    Returns:
        The  wear time info into a dictionary
    """
    # Make info dict global
    global info

    # Check if output file already exists for the current ID and get wear
    # time info only if not
    log_output_file = log_output_dir + ID_num + "_" + eval_num
    log_output_file = log_output_file + "_wear_time_info.txt"
    if os.path.exists(log_output_file) is False:
        # Read wear time log
        print("Reading wear time log file:", log_files[i])
        log = pd.read_csv(log_data_dir + log_files[i])
        # Get info from log
        info = {"duration": [], "week_day": [], "start": [], "end": []}
        for j in range(0, len(log.index)):
            info["duration"].append(log.iloc[j, 6])
            info["week_day"].append(str(log.iloc[j, 3])[:3])
            info["start"].append(log.iloc[j, 7] - 1)
            info["end"].append(log.iloc[j, 8] - 1)
        print("Writing wear time info")
        # Writing info dict in to a file
        with open(log_output_file, "wb") as handle:
            pickle.dump(info, handle)
        print("File written: " + ID_num + "_" +
              eval_num + "_wear_time_info.txt")
    else:
        message = "File " + ID_num + "_" + eval_num + "_wear_time_info.txt"
        message = message + " already exists"
        print(message)


def filter_acc_signal(sig, samp_freq=100):
    """
    Filters the acceleration signal using a Butterworth 4th order low pass
    filter with 20Hz cutoff frequency.

    Args:
        sig: A ndarray with the acceleration signal
        samp_freq: An interger with the accelerometer sample frequency.
            Defaults to 100.

    Returns:
        A ndarray with the filtered acceleration signal.
    """
    # Create the lowpass filter
    N = 4  # Filter order
    cutoff = 20  # cut-off frequency (Hz)
    fnyq = samp_freq / 2  # Nyquist frequency
    Wn = cutoff / fnyq  # Filter parameter
    b, a = signal.butter(N, Wn, btype="low")

    # Process signal
    sig = signal.filtfilt(b, a, sig)

    return sig


def main(data_dir, output_dir, acc_component, samp_freq=100,
         min_peak_height=1.3):
    """
    Main function. Set data and output directory paths using the set_pahts()
    function, loops through all files, find the acceleration peaks and writes
    the acceleration peaks and the wear time info dictionary.

    Args:
        data_dir: A character string with the path to the data directory
        output_dir: A character string with the path to the output directory
        acc_component: A character string indicating the acceleration vector
            to be used. Values can be resultant or vertical.
        samp_freq: An interger with the acceleromter sample frequency. Defaults
            to 100Hz.
        min_peak_height: A float with the minimum acceleration value (in g) to
            be considered a peak. Defaults to 1.3g.

    Returns:
        Writes the acceleration peaks and wear time info dictionary into txt
        files.
    """
    set_pahts(data_dir, output_dir)

    if acc_component not in ("resultant", "vertical"):
        raise ValueError("acc_component value must be resultant or vertical")

    # Process raw data
    for i in range(0, len(log_files)):
        print("\nProcessing file", i + 1, "out of", len(log_files))

        # Get info from file name
        ID_num = log_files[i][:3]
        eval_num = log_files[i][4:7]

        get_wear_time_info(i, ID_num, eval_num)

        # Check if output file already exists for the current ID and process
        # the raw acceleration only if not
        raw_output_file = raw_output_dir + ID_num + "_" + eval_num
        raw_output_file = raw_output_file + "_acc_peaks.txt"
        if os.path.exists(raw_output_file) is False:
            # Read raw data file
            print("Reading raw accelerometer data file:", raw_files[i])
            start_time = time.time()
            data = pd.read_csv(raw_data_dir + raw_files[i])
            time_dur = round((time.time() - start_time), 1)
            print("Reading took %s seconds" % time_dur)

            # Filter acceleration
            if acc_component == "resultant":
                # Put each axis into a ndarray
                aX = data.iloc[:, 0].to_numpy()
                aY = data.iloc[:, 1].to_numpy()
                aZ = data.iloc[:, 2].to_numpy()

                # Filter acceleration signal
                print("Filtering acceleration signal")
                start_time = time.time()
                aX = filter_acc_signal(aX)
                aY = filter_acc_signal(aY)
                aZ = filter_acc_signal(aZ)
                time_dur = round((time.time() - start_time), 1)
                print("Filtering took %s seconds" % time_dur)

                # Compute resultant vector
                aR = np.sqrt(aX ** 2 + aY ** 2 + aZ ** 2)
            elif acc_component == "vertical":
                # Put vertical axes into a ndarray
                aX = data.iloc[:, 0].to_numpy()

                # Filter acceleration signal
                print("Filtering acceleration signal")
                start_time = time.time()
                aX = filter_acc_signal(aX)
                time_dur = round((time.time() - start_time), 1)
                print("Filtering took %s seconds" % time_dur)

            # Group wear time blocks in a dictionary
            print("Grouping the acceleration signal into wear time blocks")
            blocks = {}
            if acc_component == "resultant":
                for j in range(0, len(info["start"])):
                    key_name = "resultant_" + str(j + 1)
                    blocks[key_name] = aR[info["start"][j]:info["end"][j]]
            elif acc_component == "vertical":
                for j in range(0, len(info["start"])):
                    key_name = "vertical_" + str(j + 1)
                    blocks[key_name] = aX[info["start"][j]:info["end"][j]]

            # Find peaks for all blocks
            # Peaks criteria
            height = min_peak_height
            distance = 0.4 * samp_freq  # seconds * sampling frequency
            # Find peaks
            for j in range(0, len(blocks)):
                print("Finding peaks for block", str(j + 1))
                acc_signal = blocks[list(blocks)[j]]
                peaks, properties = signal.find_peaks(acc_signal,
                                                      height=height,
                                                      distance=distance)
                # Substitute acceleration signal by peaks magnitude in the dict
                blocks[list(blocks)[j]] = properties["peak_heights"]

            # Write blocks dictionary into a file
            print("Writing the acceleration peaks magnitude into a file")
            with open(raw_output_file, "wb") as handle:
                pickle.dump(blocks, handle)
            print("File written:", ID_num + "_" + eval_num + "_acc_peaks.txt")
        else:
            message = "\nFile " + ID_num + "_" + eval_num + "_acc_peaks.txt"
            message = message + " already exists"
            print(message)

    print("Done!")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
