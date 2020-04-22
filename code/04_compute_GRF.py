import sys
from glob import glob
import os
import pickle
import pandas as pd
import numpy as np


def compute_GRF(data_dir, output_dir):
    # Set pahts
    body_mass_path = data_dir + "body_mass.txt"
    info_data_dir = output_dir + "part3_wear_time_info/"
    acc_data_dir = output_dir + "part4_acc_peaks/"
    acc_output_dir = output_dir + "part5_GRF/"

    # Create output directory if it does not exist
    if os.path.exists(acc_output_dir) is False:
        os.mkdir(acc_output_dir)

    # Read body mass data
    bm_df = pd.read_csv(body_mass_path)
    # Convert ID column to str with 3 characters
    bm_df["ID"] = bm_df["ID"].apply(str)
    for i in range(0, len(bm_df.index)):
        if len(bm_df.loc[i, "ID"]) == 2:
            bm_df.loc[i, "ID"] = "0" + bm_df.loc[i, "ID"]
        elif len(bm_df.loc[i, "ID"]) == 1:
            bm_df.loc[i, "ID"] = "00" + bm_df.loc[i, "ID"]

    # List files
    info_files = [os.path.basename(x) for x in glob(info_data_dir + "*.txt")]
    acc_files = [os.path.basename(x) for x in glob(acc_data_dir + "*.txt")]

    # Check if there are the same number of info and acc files
    if len(info_files) == len(acc_files) is False:
        raise ValueError
        print("There is a different number of info and acc files")

    # Compute GRF
    for i in range(0, len(acc_files)):
        print("Processing file", i + 1, "out of", len(acc_files))
        # Get info from file name
        ID_num = acc_files[i][:3]
        eval_num = acc_files[i][4:7]

        # Get subject body mass
        # Find index corresponding to the current subject in the bm_df
        ID_idx = list(np.where((bm_df["ID"] == ID_num) &
                      (bm_df["eval"] == eval_num)))
        # Check if there is only one index corresponding to the subject,
        # otherwise there was an error
        if len(ID_idx) > 1:
            raise ValueError
            print("More than one entry for the same subject was found in the "
                  "body_mass.txt file")
        if len(ID_idx) == 0:
            raise ValueError
            print("No entry was found for the current subject in the "
                  "body_mass.txt file")
        ID_idx = int(ID_idx[0])

        body_mass = bm_df.loc[ID_idx, "body_mass"]

        # Read wear time info
        with open(info_data_dir + info_files[i], "rb") as handle:
            info = pickle.loads(handle.read())

        # Read acc peaks file
        print("Reading acceleration peaks file:", acc_files[i])
        with open(acc_data_dir + acc_files[i], "rb") as handle:
            acc_peaks = pickle.loads(handle.read())

        # Equation coefficients
        b0 = - 698.7031  # intercept
        b1 = 1047.5129  # acc
        b2 = - 345.2605  # acc2
        b3 = 3.8294  # body mass
        b4 = 6.0219  # body mass * acc

        thrsh = 3  # threshold for maximum acceleration value in calibration

        # Initialize dictionary with variables of interest
        d = {"ID": [],
             "eval": [],
             "week_day": [],
             "duration": [],
             "n_peaks": [],
             "n_threshold": [],
             "min_peaks": [],
             "max_peaks": [],
             "mean_peaks": [],
             "sd_peaks": [],
             "sum_peaks": []}
        # Compute GRF for all of the wear time blocks
        for j in range(0, len(acc_peaks)):
            print("Computing ground reaction forces for block", str(j + i))
            # Compute GRF
            acc = acc_peaks[list(acc_peaks)[j]]
            GRF = b0 + (b1 * acc) + (b2 * (acc ** 2)) + (b3 * body_mass) \
                + (b4 * body_mass * acc)

            # Fill variables
            d["ID"].append(ID_num)
            d["eval"].append(eval_num)
            d["week_day"].append(info["week_day"][j])
            d["duration"].append(info["duration"][j])
            d["n_peaks"].append(len(acc))
            d["n_threshold"].append(len(np.where(acc > thrsh)[0]))
            d["min_peaks"].append(min(GRF))
            d["max_peaks"].append(max(GRF))
            d["mean_peaks"].append(np.mean(GRF))
            d["sd_peaks"].append(np.std(GRF))
            d["sum_peaks"].append(np.sum(GRF))

        # Check if dataframe is already in a file, if not, write a new
        if os.path.exists(acc_output_dir + "GRF_data.csv") is False:
            # Put dict into a dataframe
            df = pd.DataFrame(d)
            # Write a csv file
            df.to_csv(acc_output_dir + "GRF_data.csv", index=False)
        else:
            # If file already exists, read it and append the new values
            df = pd.read_csv(acc_output_dir + "GRF_data.csv")
            # If the current ID and eval already exists in the file,
            # overwrite it
            idx = np.where((df["ID"] == int(ID_num)) &
                           (df["eval"] == eval_num))
            if idx[0].size > 0:
                exists = True
            elif idx[0].size == 0:
                exists = False
            if exists is True:
                # Remove row indices associated with the current ID and eval
                idx = idx[0]
                df = df.drop(idx, axis="rows")
                # Append new values
                df_new = pd.DataFrame(d)
                df = df.append(df_new)
                # Sort by ID
                df["ID"] = df["ID"].astype(int)
                df = df.sort_values(by=["ID", "eval"])
                # Write a csv file
                df.to_csv(acc_output_dir + "GRF_data.csv", index=False)
            elif exists is False:
                df_new = pd.DataFrame(d)
                df = df.append(df_new)
                # Sort by ID
                df["ID"] = df["ID"].astype(int)
                df = df.sort_values(by=["ID", "eval"])
                # Write a csv file
                df.to_csv(acc_output_dir + "GRF_data.csv", index=False)

    print("Done!")

if __name__ == "__main__":
    compute_GRF(sys.argv[1], sys.argv[2])
