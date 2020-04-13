# Load packages -----------------------------------------------------------

library(tidyverse)
library(PhysicalActivity)
library(read.gt3x)

# Read data ---------------------------------------------------------------

# agd file (epoch)
agd <- readActigraph("data/068_4th_60sec_epoch.agd")

# gt3x file (raw)
raw <- read.gt3x(
  "data/068_4th.gt3x", imputeZeroes = TRUE, asDataFrame = TRUE
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
if (dir.exists("data/wear_time") == FALSE) {
  dir.create("data/wear_time")
}
write_csv(summary, "data/wear_time/068.csv")

# Raw data to csv
write_csv(raw, "data/068_4th_gt3x.csv")
