import sys
from glob import glob
import os
import pickle
import pandas as pd
import numpy as np


def set_paths(data_dir, output_dir):
    # Make variables global
    global body_mass_path
    global info_data_dir
    global info_files
    global acc_data_dir
    global acc_output_dir
    global acc_files

    # Set pahts
    body_mass_path = data_dir + "body_mass.txt"
    info_data_dir = output_dir + "part3_wear_time_info/"
    acc_data_dir = output_dir + "part3_acc_peaks/"
    acc_output_dir = output_dir + "part4_GRF/"

    # Create output directory if it does not exist
    if os.path.exists(acc_output_dir) is False:
        os.mkdir(acc_output_dir)

    # List files
    info_files = [os.path.basename(x) for x in glob(info_data_dir + "*.txt")]
    acc_files = [os.path.basename(x) for x in glob(acc_data_dir + "*.txt")]

    # Check if there are the same number of info and acc files
    if len(info_files) == len(acc_files) is False:
        raise ValueError
        print("There is a different number of info and acc files")


def get_body_mass(bm_df, ID_num, eval_num):
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

    return body_mass


def get_equation_coefficients(GRF_component, acc_placement):
    # Make variables global
    global b0  # intercept
    global b1  # acc
    global b2  # acc2
    global b3  # body mass
    global b4  # body mass * acc
    global thrsh  # threshold for maximum acceleration value in calibration

    # Check arguments values
    if GRF_component not in ("resultant", "vertical"):
        raise ValueError("GRF_component value must be resultant or vertical")
    if acc_placement not in ("hip", "back"):
        raise ValueError("acc_placement value must be back or hip")

    # Equation coefficients
    if GRF_component == "resultant" and acc_placement == "back":
        b0 = - 698.7031
        b1 = 1047.5129
        b2 = - 345.2605
        b3 = 3.8294
        b4 = 6.0219
        thrsh = 2.5
    elif GRF_component == "vertical" and acc_placement == "back":
        b0 = - 776.8934
        b1 = 1042.9052
        b2 = - 336.2115
        b3 = 6.213
        b4 = 5.0805
        thrsh = 2.5
    elif GRF_component == "resultant" and acc_placement == "hip":
        b0 = - 300.9909
        b1 = 522.6850
        b2 = - 171.5606
        b3 = 3.9596
        b4 = 5.3671
        thrsh = 3
    elif GRF_component == "vertical" and acc_placement == "hip":
        b0 = - 435.7365
        b1 = 586.6627
        b2 = - 188.9689
        b3 = 5.8047
        b4 = 4.9544
        thrsh = 3


def compute_GRF(acc, body_mass, GRF_component, acc_placement):
    get_equation_coefficients(GRF_component, acc_placement)

    GRF = b0 + (b1 * acc) + (b2 * (acc ** 2)) + (b3 * body_mass) \
        + (b4 * body_mass * acc)

    return GRF


def summarize_GRF(ID_num, eval_num, info, acc_peaks, body_mass,
                  GRF_component, acc_placement):

    # Initialize dictionary with variables of interest
    d = {"ID": [],
         "eval": [],
         "acc_placement": [],
         "GRF_component": [],
         "week_day": [],
         "duration": [],
         "n_peaks": [],
         "n_threshold": [],
         "min_peaks": [],
         "max_peaks": [],
         "mean_peaks": [],
         "sd_peaks": [],
         "sum_peaks": []}

    if GRF_component in ("resultant", "vertical"):
        # Compute GRF for all of the wear time blocks using one of the
        # components
        for i in range(0, len(acc_peaks)):
            print("Computing ground reaction forces for block", str(i + 1))
            # Compute GRF
            acc = acc_peaks[list(acc_peaks)[i]]
            GRF = compute_GRF(acc, body_mass, GRF_component, acc_placement)
            # Fill variables
            d["ID"].append(ID_num)
            d["eval"].append(eval_num)
            d["acc_placement"].append(acc_placement)
            d["GRF_component"].append(GRF_component)
            d["week_day"].append(info["week_day"][i])
            d["duration"].append(info["duration"][i])
            d["n_peaks"].append(len(acc))
            d["n_threshold"].append(len(np.where(acc > thrsh)[0]))
            d["min_peaks"].append(min(GRF))
            d["max_peaks"].append(max(GRF))
            d["mean_peaks"].append(np.mean(GRF))
            d["sd_peaks"].append(np.std(GRF))
            d["sum_peaks"].append(np.sum(GRF))
    else:
        raise ValueError("GRF_component value must be resultant or vertical")

    return d


def write_GRF_data(ID_num, eval_num, data):
    # Check if dataframe is already in a file, if not, write a new
    if os.path.exists(acc_output_dir + "GRF_data.csv") is False:
        # Put dict into a dataframe
        df = pd.DataFrame(data)
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
            df_new = pd.DataFrame(data)
            df = df.append(df_new)
            # Sort by ID
            df["ID"] = df["ID"].astype(int)
            df = df.sort_values(by=["ID", "eval", "acc_placement",
                                    "GRF_component"])
            # Write a csv file
            df.to_csv(acc_output_dir + "GRF_data.csv", index=False)
        elif exists is False:
            df_new = pd.DataFrame(data)
            df = df.append(df_new)
            # Sort by ID
            df["ID"] = df["ID"].astype(int)
            df = df.sort_values(by=["ID", "eval"])
            # Write a csv file
            df.to_csv(acc_output_dir + "GRF_data.csv", index=False)


def main(data_dir, output_dir, GRF_component, acc_placement):
    set_paths(data_dir, output_dir)

    # Read body mass data
    bm_df = pd.read_csv(body_mass_path)
    # Convert ID column to str with 3 characters
    bm_df["ID"] = bm_df["ID"].apply(str)
    for i in range(0, len(bm_df.index)):
        if len(bm_df.loc[i, "ID"]) == 2:
            bm_df.loc[i, "ID"] = "0" + bm_df.loc[i, "ID"]
        elif len(bm_df.loc[i, "ID"]) == 1:
            bm_df.loc[i, "ID"] = "00" + bm_df.loc[i, "ID"]

    # Compute GRF
    for i in range(0, len(acc_files)):
        print("Processing file", i + 1, "out of", len(acc_files))
        # Get info from file name
        ID_num = acc_files[i][:3]
        eval_num = acc_files[i][4:7]

        # Get subject body mass
        body_mass = get_body_mass(bm_df, ID_num, eval_num)

        # Read wear time info
        with open(info_data_dir + info_files[i], "rb") as handle:
            info = pickle.loads(handle.read())

        # Read acc peaks file
        print("Reading acceleration peaks file:", acc_files[i])
        with open(acc_data_dir + acc_files[i], "rb") as handle:
            acc_peaks = pickle.loads(handle.read())

        # Compute ground reaction force and summarize values into a dict
        d = summarize_GRF(ID_num, eval_num, info, acc_peaks, body_mass,
                          GRF_component, acc_placement)

        # Write summarized data into a csv file
        write_GRF_data(ID_num, eval_num, d)

    print("Done!")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
