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
        raise ValueError("There is a different number of info and acc files")


def get_body_mass(bm_df, ID_num, eval_num):
    # Find index corresponding to the current subject in the bm_df
    ID_idx = list(np.where((bm_df["ID"] == ID_num) &
                  (bm_df["eval"] == eval_num)))
    # Check if there is only one index corresponding to the subject,
    # otherwise there was an error
    if len(ID_idx) > 1:
        raise ValueError("More than one entry for the same subject was found "
                         "in the body_mass.txt file")
    if len(ID_idx) == 0:
        raise ValueError("No entry was found for the current subject in the "
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
    elif GRF_component == "vertical" and acc_placement == "back":
        b0 = - 776.8934
        b1 = 1042.9052
        b2 = - 336.2115
        b3 = 6.213
        b4 = 5.0805
    elif GRF_component == "resultant" and acc_placement == "hip":
        b0 = - 300.9909
        b1 = 522.6850
        b2 = - 171.5606
        b3 = 3.9596
        b4 = 5.3671
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


def get_pks_interval(data, lim1, lim2):
    if lim2 is None:
        peaks_interval = np.where(data >= lim1)[0]
    else:
        peaks_interval = np.where((data > lim1) & (data <= lim2))[0]

    return peaks_interval


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
         "min_peaks_N": [],
         "max_peaks_N": [],
         "mean_peaks_N": [],
         "sd_peaks_N": [],
         "sum_peaks_N": [],
         "n_g_1.2-1.4": [],
         "n_g_1.4-1.6": [],
         "n_g_1.6-1.8": [],
         "n_g_1.8-2.0": [],
         "n_g_2.0-2.2": [],
         "n_g_2.2-2.4": [],
         "n_g_2.4-2.6": [],
         "n_g_2.6-2.8": [],
         "n_g_2.8-3.0": [],
         "n_g_3.0-4.0": [],
         "n_g_4.0-5.0": [],
         "n_g_5.0-6.0": [],
         "n_g_6.0-7.0": [],
         "n_g_7.0-8.0": [],
         "n_g_8.0-9.0": [],
         "n_g_9.0": [],
         "sum_GRF_N_g_1.2-1.4": [],
         "sum_GRF_N_g_1.4-1.6": [],
         "sum_GRF_N_g_1.6-1.8": [],
         "sum_GRF_N_g_1.8-2.0": [],
         "sum_GRF_N_g_2.0-2.2": [],
         "sum_GRF_N_g_2.2-2.4": [],
         "sum_GRF_N_g_2.4-2.6": [],
         "sum_GRF_N_g_2.6-2.8": [],
         "sum_GRF_N_g_2.8-3.0": [],
         "min_peaks_BW": [],
         "max_peaks_BW": [],
         "mean_peaks_BW": [],
         "sd_peaks_BW": [],
         "sum_peaks_BW": [],
         "n_BW_1.0-1.1": [],
         "n_BW_1.1-1.2": [],
         "n_BW_1.2-1.3": [],
         "n_BW_1.3-1.4": [],
         "n_BW_1.4-1.5": [],
         "n_BW_1.5-1.6": [],
         "n_BW_1.6-1.7": [],
         "n_BW_1.7-1.8": [],
         "n_BW_1.8": [],
         "sum_GRF_N_BW_1.0-1.1": [],
         "sum_GRF_N_BW_1.1-1.2": [],
         "sum_GRF_N_BW_1.2-1.3": [],
         "sum_GRF_N_BW_1.3-1.4": [],
         "sum_GRF_N_BW_1.4-1.5": [],
         "sum_GRF_N_BW_1.5-1.6": [],
         "sum_GRF_N_BW_1.6-1.7": [],
         "sum_GRF_N_BW_1.7-1.8": [],
         "sum_GRF_N_BW_1.8": []}

    if GRF_component in ("resultant", "vertical"):
        # Compute GRF for all of the wear time blocks using one of the
        # components
        for i in range(0, len(acc_peaks)):
            print("Computing ground reaction forces for block", str(i + 1))
            # Compute GRF
            acc = acc_peaks[list(acc_peaks)[i]]
            # Compute ground reaction force (in N)
            GRF = compute_GRF(acc, body_mass, GRF_component, acc_placement)
            # Get number of peaks above the threshold
            n_threshold = len(np.where(acc > thrsh)[0])
            # Remove those peaks from the GRF array
            GRF = np.delete(GRF, np.where(acc > thrsh)[0])
            # Create an acc array with the peaks above threshold removed
            acc_new = np.delete(acc, np.where(acc > thrsh)[0])
            # Compute ground reaction force (in BW)
            BW = GRF / (body_mass * 9.81)
            # Fill variables
            d["ID"].append(ID_num)
            d["eval"].append(eval_num)
            d["acc_placement"].append(acc_placement)
            d["GRF_component"].append(GRF_component)
            d["week_day"].append(info["week_day"][i])
            d["duration"].append(info["duration"][i])
            d["n_peaks"].append(len(acc))
            if len(acc) == 0:
                d["n_threshold"].append(0)
                d["min_peaks_N"].append(0)
                d["max_peaks_N"].append(0)
                d["mean_peaks_N"].append(0)
                d["sd_peaks_N"].append(0)
                d["sum_peaks_N"].append(0)
                d["min_peaks_N"].append(0)
                d["max_peaks_BW"].append(0)
                d["mean_peaks_BW"].append(0)
                d["sd_peaks_BW"].append(0)
                d["sum_peaks_BW"].append(0)
            else:
                d["n_threshold"].append(n_threshold)
                d["min_peaks_N"].append(min(GRF))
                d["max_peaks_N"].append(max(GRF))
                d["mean_peaks_N"].append(np.mean(GRF))
                d["sd_peaks_N"].append(np.std(GRF))
                d["sum_peaks_N"].append(np.sum(GRF))
                d["n_g_1.2-1.4"].append(len(get_pks_interval(acc, 1.2, 1.4)))
                d["n_g_1.4-1.6"].append(len(get_pks_interval(acc, 1.4, 1.6)))
                d["n_g_1.6-1.8"].append(len(get_pks_interval(acc, 1.6, 1.8)))
                d["n_g_1.8-2.0"].append(len(get_pks_interval(acc, 1.8, 2.0)))
                d["n_g_2.0-2.2"].append(len(get_pks_interval(acc, 2.0, 2.2)))
                d["n_g_2.2-2.4"].append(len(get_pks_interval(acc, 2.2, 2.4)))
                d["n_g_2.4-2.6"].append(len(get_pks_interval(acc, 2.4, 2.6)))
                d["n_g_2.6-2.8"].append(len(get_pks_interval(acc, 2.6, 2.8)))
                d["n_g_2.8-3.0"].append(len(get_pks_interval(acc, 2.8, 3.0)))
                d["n_g_3.0-4.0"].append(len(get_pks_interval(acc, 3.0, 4.0)))
                d["n_g_4.0-5.0"].append(len(get_pks_interval(acc, 4.0, 5.0)))
                d["n_g_5.0-6.0"].append(len(get_pks_interval(acc, 5.0, 6.0)))
                d["n_g_6.0-7.0"].append(len(get_pks_interval(acc, 6.0, 7.0)))
                d["n_g_7.0-8.0"].append(len(get_pks_interval(acc, 7.0, 8.0)))
                d["n_g_8.0-9.0"].append(len(get_pks_interval(acc, 8.0, 9.0)))
                d["n_g_9.0"].append(len(get_pks_interval(acc, 9.0, None)))
                d["sum_GRF_N_g_1.2-1.4"].append(sum(GRF[get_pks_interval(
                                                acc_new, 1.2, 1.4)]))
                d["sum_GRF_N_g_1.4-1.6"].append(sum(GRF[get_pks_interval(
                                                acc_new, 1.4, 1.6)]))
                d["sum_GRF_N_g_1.6-1.8"].append(sum(GRF[get_pks_interval(
                                                acc_new, 1.6, 1.8)]))
                d["sum_GRF_N_g_1.8-2.0"].append(sum(GRF[get_pks_interval(
                                                acc_new, 1.8, 2.0)]))
                d["sum_GRF_N_g_2.0-2.2"].append(sum(GRF[get_pks_interval(
                                                acc_new, 2.0, 2.2)]))
                d["sum_GRF_N_g_2.2-2.4"].append(sum(GRF[get_pks_interval(
                                                acc_new, 2.2, 2.4)]))
                d["sum_GRF_N_g_2.4-2.6"].append(sum(GRF[get_pks_interval(
                                                acc_new, 2.4, 2.6)]))
                d["sum_GRF_N_g_2.6-2.8"].append(sum(GRF[get_pks_interval(
                                                acc_new, 2.6, 2.8)]))
                d["sum_GRF_N_g_2.8-3.0"].append(sum(GRF[get_pks_interval(
                                                acc_new, 2.8, 3.0)]))
                d["min_peaks_BW"].append(min(BW))
                d["max_peaks_BW"].append(max(BW))
                d["mean_peaks_BW"].append(np.mean(BW))
                d["sd_peaks_BW"].append(np.std(BW))
                d["sum_peaks_BW"].append(np.sum(BW))
                d["n_BW_1.0-1.1"].append(len(get_pks_interval(BW, 1.0, 1.1)))
                d["n_BW_1.1-1.2"].append(len(get_pks_interval(BW, 1.1, 1.2)))
                d["n_BW_1.2-1.3"].append(len(get_pks_interval(BW, 1.2, 1.3)))
                d["n_BW_1.3-1.4"].append(len(get_pks_interval(BW, 1.3, 1.4)))
                d["n_BW_1.4-1.5"].append(len(get_pks_interval(BW, 1.4, 1.5)))
                d["n_BW_1.5-1.6"].append(len(get_pks_interval(BW, 1.5, 1.6)))
                d["n_BW_1.6-1.7"].append(len(get_pks_interval(BW, 1.6, 1.7)))
                d["n_BW_1.7-1.8"].append(len(get_pks_interval(BW, 1.7, 1.8)))
                d["n_BW_1.8"].append(len(get_pks_interval(BW, 1.8, None)))
                d["sum_GRF_N_BW_1.0-1.1"].append(sum(BW[get_pks_interval(BW, 1.0, 1.1)]))
                d["sum_GRF_N_BW_1.1-1.2"].append(sum(BW[get_pks_interval(BW, 1.1, 1.2)]))
                d["sum_GRF_N_BW_1.2-1.3"].append(sum(BW[get_pks_interval(BW, 1.2, 1.3)]))
                d["sum_GRF_N_BW_1.3-1.4"].append(sum(BW[get_pks_interval(BW, 1.3, 1.4)]))
                d["sum_GRF_N_BW_1.4-1.5"].append(sum(BW[get_pks_interval(BW, 1.4, 1.5)]))
                d["sum_GRF_N_BW_1.5-1.6"].append(sum(BW[get_pks_interval(BW, 1.5, 1.6)]))
                d["sum_GRF_N_BW_1.6-1.7"].append(sum(BW[get_pks_interval(BW, 1.6, 1.7)]))
                d["sum_GRF_N_BW_1.7-1.8"].append(sum(BW[get_pks_interval(BW, 1.7, 1.8)]))
                d["sum_GRF_N_BW_1.8"].append(sum(BW[get_pks_interval(BW, 1.8, None)]))
    else:
        raise ValueError("GRF_component value must be resultant or vertical")

    return d


def write_GRF_data(ID_num, eval_num, data):
    # Check if dataframe is already in a file, if not, write a new
    if os.path.exists(acc_output_dir + "GRF_data.csv") is False:
        # Put dict into a dataframe
        df = pd.DataFrame(data)
        df = df.sort_values(by=["ID", "eval", "acc_placement",
                                "GRF_component"])
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
            df = df.sort_values(by=["ID", "eval", "acc_placement",
                                    "GRF_component"])
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
