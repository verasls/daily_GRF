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
  gt3x_data_dir <<- str_c(data_dir, "gt3x/", sep = "")
  gt3x_output_dir <<- str_c(output_dir, "part1_raw_acc_data/", sep = "")
  
  # Create output directory if it does not exist
  if (dir.exists(gt3x_output_dir) == FALSE) {
    dir.create(gt3x_output_dir, recursive = TRUE)
  }
  
  # List files in data directory
  files <<- list.files(gt3x_data_dir)
}

convert_gt3x <- function(files, gt3x_data_dir, gt3x_output_dir) {
  # Reads the raw accelerometer gt3x file and writes it into a txt file.
  #
  # Args:
  #   gt3x_data_dir: a character string with the path to the gt3x data directory
  #   gt3x_output_dir: a character string with the path to the gt3x output 
  #     directory
  #
  # Returns:
  #  Writes the raw accelerometer gt3x file into a txt file.

  suppressPackageStartupMessages(require(stringr))
  suppressPackageStartupMessages(require(read.gt3x))
  suppressPackageStartupMessages(require(data.table))
  
  # Converting gt3x into txt
  for (i in 1:length(files)) {
    # Get info from file name
    ID_num <- str_sub(files[i], 1, 3)
    eval_num <- str_sub(files[i], 5, 7)
    
    # Check if output file already exists for the current ID and convert the file
    # only if not
    output_file <- str_c(ID_num, eval_num, "raw.txt", sep = "_")
    output_path <- str_c(gt3x_output_dir, output_file, sep = "")
    if (file.exists(output_path) == FALSE) {
      message <- str_c(
        "\nReading file ", i, " out of ", length(files), 
        ": ", files[i], "\n", sep = ""
      )
      cat(message)
      # Read gt3x file (raw)
      start_time <- Sys.time()
      data_file <- str_c(gt3x_data_dir, files[i], sep = "")
      gt3x <- read.gt3x(
        data_file, imputeZeroes = TRUE, asDataFrame = TRUE
      )
      end_time <- Sys.time()
      time <- round(as.numeric(difftime(end_time, start_time, units = "secs")), 1)
      message <- str_c("Reading took ", time, " seconds\n", sep = "")
      cat(message)
      
      # Select only the acc axes
      gt3x <- gt3x[, 1:3]
      
      cat("Converting gt3x into txt\n")
      # Write raw data into a txt file    
      start_time <- Sys.time()
      fwrite(gt3x, output_path)
      end_time <- Sys.time()
      time <- round(as.numeric(difftime(end_time, start_time, units = "secs")), 1)
      message <- str_c("Conversion took ", time, " seconds\n", sep = "")
      cat(message)
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
  # function and converts the raw accelerometer data files using the 
  # convert_gt3x() function.
  #
  # Args:
  #   data_dir: a character string with the path to the data directory
  #   output_dir: a character string with the path to the output directory
  #
  # Returns:
  #  Writes the raw accelerometer gt3x file into a txt file.

  set_paths(data_dir, output_dir)
  convert_gt3x(files, gt3x_data_dir, gt3x_output_dir)
}

if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
	data_dir <- args[1]
	output_dir <- args[2]  
	main(data_dir, output_dir)
}
