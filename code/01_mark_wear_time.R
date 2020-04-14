# Load packages -----------------------------------------------------------

library(tidyverse)
library(PhysicalActivity)
library(read.gt3x)

# Read data ---------------------------------------------------------------

data_dir <- "/Volumes/LVERAS/data/"
agd_path <- paste(data_dir, "068_4th_60sec_epoch.agd", sep = "")
raw_path <- paste(data_dir, "068_4th.gt3x", sep = "")

# agd file (epoch)
agd <- readActigraph(agd_path)

# gt3x file (raw)
raw <- read.gt3x(
  raw_path, imputeZeroes = TRUE, asDataFrame = TRUE
)

# Process -----------------------------------------------------------------

# Mark wear and non-wear time using agd epoch file
marked <- wearingMarking(
  dataset = agd,
  frame = 90,
  perMinuteCts = 1,
  getMinuteMarking = TRUE
)

# Summarise
summary <- sumVct(datavct = marked) %>% as_tibble()
summary$weekday <- str_to_upper(summary$weekday)
summary$weekday <- as_factor(summary$weekday)
# Get start and end lines for raw data (to be used in python script)
summary <- summary %>% 
  mutate(
    start_idx = (start * 60 * 100) - (59 * 100),
    end_idx = (end * 60 * 100) - (59 * 100)
  )

# Get wear time per day (min)
summary %>% 
  group_by(weekday) %>% 
  summarise(wear_time = sum(duration))

# Export ------------------------------------------------------------------

# Wear time log 
wt_dir <- paste(data_dir, "wear_time/", sep = "")
if (dir.exists(wt_dir) == FALSE) {
  dir.create(wt_dir)
}
write_csv(summary, paste(wt_dir, "068.csv", sep = ""))

# Raw data
# Select only the acc axes
raw <- raw[, 1:3]
# Write into a txt file
write_delim(
  raw, 
  paste(data_dir, "068_4th_raw.txt", sep = ""), 
  delim = ","
)
