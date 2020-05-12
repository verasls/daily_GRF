set_paths <- function(data_dir, output_dir) {
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
  agd_data_dir <<- str_c(data_dir, "agd/", sep = "")
  agd_output_dir <<- str_c(output_dir, "part2_wear_time_logs/", sep = "")
  
  # Create output directory if it does not exist
  if (dir.exists(agd_output_dir) == FALSE) {
    dir.create(agd_output_dir, recursive = TRUE)
  }
  
  # List files in data directory
  files <<- list.files(agd_data_dir)  
}

mark_wear_time <- function(files, agd_data_dir, agd_output_dir) {
  # Reads the accelerometer agd files and detects wear and non-wear time.
  # Accelerometer files must be in 60 sec epochs.
  #
  # Args:
  #   agd_data_dir: a character string with the path to the agd data directory
  #   agdx_output_dir: a character string with the path to the agd output 
  #     directory
  #
  # Returns:
  # Writes a txt file wirh summary information of the wear time periods. 

  suppressPackageStartupMessages(require(stringr))
  suppressPackageStartupMessages(require(dplyr))
  suppressPackageStartupMessages(require(PhysicalActivity))
  suppressPackageStartupMessages(require(data.table))
  
  # Mark wear time
  for (i in 1:length(files)) {
    message <- str_c(
      "\nReading file ", i, " out of ", length(files), 
      ": ", files[i], "\n", sep = ""
    )
    cat(message)
    
    # Get info from file name
    ID_num <- str_sub(files[i], 1, 3)
    eval_num <- str_sub(files[i], 5, 7)
    
    # Check if output file already exists for the current ID and mark wear time
    # only if not
    output_file <- str_c(ID_num, eval_num, "wear_time_log.txt", sep = "_")
    output_path <- str_c(agd_output_dir, output_file, sep = "")
    if (file.exists(output_path) == FALSE) {
      # Read agd file
      data_file <- str_c(agd_data_dir, files[i], sep = "")
      agd <- readActigraph(data_file)
      
      # Mark wear and non-wear time using agd epoch file
      cat("Marking wear time\n")
      invisible(capture.output(marked <- wearingMarking(
        dataset = agd,
        frame = 90,
        perMinuteCts = 1,
        cts = "vm",
        streamFrame = 10,
        allowanceFrame = 2
      )))
      
      # Summarise wear time information
      wear_time_log <- sumVct(datavct = marked)
      wear_time_log$weekday <- str_to_lower(wear_time_log$weekday)
      
      # Get start and end lines for raw data (to be used in python script)
      wear_time_log <- wear_time_log %>% 
        mutate(
          start_idx = (start * 60 * 100) - (59 * 100),
          end_idx = (end * 60 * 100) - (59 * 100)
        )
      
      # Write log into txt
      cat("Writing wear time log\n")
      fwrite(wear_time_log, output_path)
      message <- str_c("File written: ", output_file, "\n", sep = "")
      cat(message) 
    } else {
      message <- str_c(
        "\nFile ", files[i], " has already been processed\n", sep = ""
      )
      cat(message)
    }
  }
  
  cat("Done!\n")
}

main <- function(data_dir, output_dir) {
  # Main function. Set data and output directory paths using set_paths() 
  # function and writes wear time log info into txt files using the 
  # mark_wear_time() function.
  #
  # Args:
  #   data_dir: a character string with the path to the data directory
  #   output_dir: a character string with the path to the output directory
  #
  # Returns:
  #  Writes the wear time info into txt files.

  set_paths(data_dir, output_dir)
  mark_wear_time(files, agd_data_dir, agd_output_dir)
}

if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  data_dir <- args[1]
  output_dir <- args[2]  
  main(data_dir, output_dir)
}
