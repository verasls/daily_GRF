set_paths <- function(output_dir) {
  # Set data and output paths
  #
  # Args:
  #   data_dir: a character string with the path to the data directory
  #   output_dir: a character string with the path to the output directory
  #
  # Returns:
  #   Assigns the data_dir and output_dir variables to the global environment.
  #   Creates the output directory if it does not exist.

  suppressPackageStartupMessages(require(stringr))
  
  # Set paths
  grf_data_dir <<- str_c(output_dir, "part4_GRF/", sep = "")
  grf_output_dir <<- str_c(output_dir, "part5_summary_GRF/", sep = "")
  
  # Create output directory if it does not exist
  if (dir.exists(grf_output_dir) == FALSE) {
    dir.create(grf_output_dir, recursive = TRUE)
  }
  
  # List files in data directory
  files <<- list.files(grf_data_dir)  
}

filter_GRF_data <- function(min_hours_crit = 600, min_days_crit = 3) {
  # Removes from the summary GRF data frame subjects who do not have the
  # minimum of wear time hours per day or the minimum number of valid days
  #
  # Args:
  #   min_hours_crit: A numeric value with the minimum number of wear time
  #	minutes in a day. Defaults to 600 min.
  #   min_days_crit: A numeric value with the minimum number of valid days.
  #     Defaults to 3 days.
  #
  # Returns:
  #   The summary GRF data frame without the subjects who do not have the
  #   minimum number of hours on a day or the minimum number of valid days.
  suppressPackageStartupMessages(require(readr))
  suppressPackageStartupMessages(require(stringr))
  suppressPackageStartupMessages(require(magrittr))
  suppressPackageStartupMessages(require(dplyr))
  
  for (i in 1:length(files)) {
    message <- str_c(
      "\nReading file ", i, " out of ", length(files), 
      ": ", files[i], "\n", sep = ""
    )
    cat(message)
    
    # Read data and filter by min_hours_crit
    data_file <- str_c(grf_data_dir, files[i], sep = "")
    df <- suppressMessages(read_csv(data_file)) %>% 
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
    
    # Make a list of IDs that have min_days_crit
    ID_day_crit <- df %>% 
      group_by(ID) %>% 
      summarise(n_days = n()) %>% 
      filter(n_days >= min_days_crit)
    ID_day_crit <- as.double(ID_day_crit[, "ID"][[1]])
    
    # Filter by min_days_crit
    df <- df %>%
      filter(ID %in% ID_day_crit)
  }
  df <- df %>% ungroup()
  
  cat("Writing file GRF_data.csv\n")
  output_file <- str_c(grf_output_dir, "GRF_data.csv")
  write_csv(df, output_file)
  return(df)
}

summarise_GRF_data <- function(df) {
  # Collapse the data frame to contain one row per subject.
  #
  # Args:
  #   df: A data frame with the summary GRF values
  #
  # Returns:
  #   The input data frame with one row per subject. The variable values are
  #   transformed to be the average per valid day.
  suppressPackageStartupMessages(require(readr))
  suppressPackageStartupMessages(require(stringr))
  suppressPackageStartupMessages(require(magrittr))
  suppressPackageStartupMessages(require(dplyr))
  
  cat("Summarising data\n")
  df <- df %>% 
    group_by(ID, eval, acc_placement, GRF_component) %>% 
    mutate(
      n_days = n()
    ) %>% 
    summarise_if(is.numeric, mean) %>% 
    select(1:5, n_days, everything())
  
  cat("Writing file summary_GRF_data.csv\n")
  output_file <- str_c(grf_output_dir, "summary_GRF_data.csv")
  write_csv(df, output_file)
}

main <- function(output_dir) {
  # Main function. Set data and output directory paths using set_paths() 
  # function and cleans the summary GRF data frame.
  #
  # Args:
  #   output_dir: a character string with the path to the output directory
  #
  # Returns:
  #  Writes the cleaned summary data frame. 
  set_paths(output_dir)
  df <- filter_GRF_data()
  summarise_GRF_data(df)
}

if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  output_dir <- args[1]  
  main(output_dir)
}
