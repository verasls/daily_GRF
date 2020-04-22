set_paths <- function(data_dir, output_dir) {
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
        "Reading file ", i, " out of ", length(files), ": ", files[i], sep = ""
      )
      print(message)
      # Read gt3x file (raw)
      start_time <- Sys.time()
      data_file <- str_c(gt3x_data_dir, files[i], sep = "")
      gt3x <- read.gt3x(
        data_file, imputeZeroes = TRUE, asDataFrame = TRUE
      )
      end_time <- Sys.time()
      time <- round(as.numeric(difftime(end_time, start_time, units = "secs")), 1)
      message <- str_c("Reading took ", time, " seconds", sep = "")
      print(message)
      
      # Select only the acc axes
      gt3x <- gt3x[, 1:3]
      
      print("Converting gt3x into txt")
      # Write raw data into a txt file    
      start_time <- Sys.time()
      fwrite(gt3x, output_path)
      end_time <- Sys.time()
      time <- round(as.numeric(difftime(end_time, start_time, units = "secs")), 1)
      message <- str_c("Conversion took ", time, " seconds", sep = "")
      print(message)
      message <- str_c("File written: ", output_file, sep = "")
      print(message)
    } else {
      message <- str_c("File ", files[i], " has already been processed", sep = "")
      print(message)
    }
  }
  
  print("Done!")
}

main <- function(data_dir, output_dir) {
  set_paths(data_dir, output_dir)
  convert_gt3x(files, gt3x_data_dir, gt3x_output_dir)
}

if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
	data_dir <- args[1]
	output_dir <- args[2]  
	main(data_dir, output_dir)
}
