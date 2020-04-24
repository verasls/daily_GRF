library(tidyverse)

min_hours_crit <- 600
min_days_crit <- 3

df <- read_csv("/Volumes/LVERAS/daily_GRF/output/4th/part4_GRF/GRF_data.csv") %>% 
  group_by(ID, eval, acc_placement, GRF_component, week_day) %>% 
  summarize_if(is.numeric, sum, na.rm = TRUE) %>% 
  arrange(
    ID, eval, acc_placement, GRF_component,
    factor(
      week_day,
      levels = c(
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
      )
    )
  ) %>% 
  filter(duration >= min_hours_crit)


ID_day_crit <- df %>% 
  group_by(ID) %>% 
  summarise(n_days = n()) %>% 
  filter(n_days >= min_days_crit)
ID_day_crit <- ID_day_crit[, "ID"]

df <- df %>% 
  filter(ID %in% ID_day_crit)
