# Load packages -----------------------------------------------------------

suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(PhysicalActivity))

# Read data ---------------------------------------------------------------

# Getting paths -----------------------------------------------------------

# General
data_dir <- "/Volumes/LVERAS/daily_GRF/data/"
output_dir <- "/Volumes/LVERAS/daily_GRF/output/"

# Specific
agd_data <- str_c(data_dir, "agd/", sep = "")
agd_output <- str_c(output_dir, "02_wear_time_logs/", sep = "")

# Create output directory if it does not exist
if (dir.exists(agd_output) == FALSE) {
  dir.create(agd_output, recursive = TRUE)
}

# List files in data directory
files <- list.files(agd_data)

# Marking wear time -------------------------------------------------------

for (i in 1:length(files)) {
  # Read agd file
  message <- str_c(
    "Reading file ", i, " out of ", length(files), ": ", files[i], sep = ""
  )
  print(message)
  
  data_file <- str_c(agd_data, files[i], sep = "")
  agd <- readActigraph(data_file)
  
  # Mark wear and non-wear time using agd epoch file
  print("Marking wear time")
  marked <- wearingMarking(
    dataset = agd,
    frame = 90,
    perMinuteCts = 1,
    getMinuteMarking = TRUE
  )
  
  # Summarise wear time information
  wear_time_log <- sumVct(datavct = marked) %>% as_tibble()
  wear_time_log$weekday <- str_to_upper(wear_time_log$weekday)
  wear_time_log$weekday <- as_factor(wear_time_log$weekday)
  
  # Get start and end lines for raw data (to be used in python script)
  wear_time_log <- wear_time_log %>% 
    mutate(
      start_idx = (start * 60 * 100) - (59 * 100),
      end_idx = (end * 60 * 100) - (59 * 100)
    )
  
  # Write log into txt
  print("Writing wear time log")
  output_file <- str_c(str_sub(files[i], 1, 7), "_wear_time_log.txt", sep = "")
  write_delim(
    wear_time_log,
    str_c(agd_output, output_file, sep = ""),
    delim = ","
  )
  message <- str_c("File written: ", output_file, sep = "")
  print(message)
}

print("Done!")
