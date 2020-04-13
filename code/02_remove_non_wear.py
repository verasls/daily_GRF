import pandas as pd
import time


# Get path to data
data_dir = "/Volumes/LVERAS/data/"
log_path = data_dir + "wear_time/068.csv"
raw_path = data_dir + "068_4th_raw.txt"

# Read wear time log
log = pd.read_csv(log_path)

# Read raw data file
start_time = time.time()
data = pd.read_csv(raw_path)
print("pd.read_csv took %s seconds" % (time.time() - start_time))
