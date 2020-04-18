import glob
import os
import pickle
import pandas as pd
import numpy as np

# Getting paths
# General
data_dir = "/Volumes/LVERAS/daily_GRF/data/"
output_dir = "/Volumes/LVERAS/daily_GRF/output/"

# Specific
body_mass_path = data_dir + "body_mass.txt"
acc_data_dir = output_dir + "04_acc_peaks/"
acc_output_dir = output_dir + "05_GRF/"

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

# List acc peaks files
acc_files = [os.path.basename(x) for x in glob.glob(acc_data_dir + "*.txt")]


# ----- beging looping through the files here -----

# Get info from file name
ID_num = acc_files[0][:3]
eval_num = acc_files[0][4:7]

# Get subject body mass
# Find index corresponding to the current subject in the bm_df
ID_idx = list(np.where((bm_df["ID"] == ID_num) & (bm_df["eval"] == eval_num)))
# Check if there is only one index corresponding to the subject, otherwise
# there was an error
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

# Read acc peaks file
with open(acc_data_dir + acc_files[0], "rb") as handle:
    acc_peaks = pickle.loads(handle.read())
