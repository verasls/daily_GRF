# Load packages -----------------------------------------------------------

suppressPackageStartupMessages(library(tidyverse, quietly = TRUE))
suppressPackageStartupMessages(library(read.gt3x, quietly = TRUE))

# Getting paths -----------------------------------------------------------

# General
data_dir <- "/Volumes/LVERAS/daily_GRF/data/"
output_dir <- "/Volumes/LVERAS/daily_GRF/output/"

# Specific
gt3x_data_dir <- str_c(data_dir, "gt3x/", sep = "")
gt3x_output_dir <- str_c(output_dir, "01_raw_acc_data/", sep = "")

# Create output directory if it does not exist
if (dir.exists(gt3x_output_dir) == FALSE) {
  dir.create(gt3x_output_dir, recursive = TRUE)
}

# List files in data directory
files <- list.files(gt3x_data_dir)

# Converting gt3x into txt ------------------------------------------------

for (i in 1:length(files)) {
  # Get info from file name
  ID_num <- str_sub(files[i], 1, 3)
  eval_num <- str_sub(files[i], 5, 7)
  
  # Read gt3x file (raw)
  message <- str_c(
    "Reading file ", i, " out of ", length(files), ": ", files[i], sep = ""
  )
  print(message)
  
  data_file <- str_c(gt3x_data_dir, files[i], sep = "")
  gt3x <- read.gt3x(
    data_file, imputeZeroes = TRUE, asDataFrame = TRUE
  )
  # Select only the acc axes
  gt3x <- gt3x[, 1:3]
  
  print("Converting gt3x into txt")
  # Write raw data into a txt file
  output_file <- str_c(ID_num, eval_num, "raw.txt", sep = "_")
  write_delim(
    gt3x, 
    str_c(gt3x_output_dir, output_file, sep = ""), 
    delim = ","
  )
  message <- str_c("File written: ", output_file, sep = "")
  print(message)
}

print("Done!")
