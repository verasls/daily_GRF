main <- function(data_dir, output_dir) {
  suppressPackageStartupMessages(require(stringr))
  suppressPackageStartupMessages(require(dplyr))
  suppressPackageStartupMessages(require(PhysicalActivity))
  suppressPackageStartupMessages(require(data.table))

  # Set paths
  agd_data_dir <- str_c(data_dir, "agd/", sep = "")
  agd_output_dir <- str_c(output_dir, "part2_wear_time_logs/", sep = "")

  # Create output directory if it does not exist
  if (dir.exists(agd_output_dir) == FALSE) {
    dir.create(agd_output_dir, recursive = TRUE)
  }
  
  # List files in data directory
  files <- list.files(agd_data_dir)
  
  # Mark wear time
  
  for (i in 1:length(files)) {
    message <- str_c(
      "Reading file ", i, " out of ", length(files), ": ", files[i], sep = ""
    )
    print(message)
    
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
      print("Marking wear time")
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
      print("Writing wear time log")
      fwrite(wear_time_log, output_path)
      message <- str_c("File written: ", output_file, sep = "")
      print(message) 
    } else {
      message <- str_c("File ", files[i], " has already been processed", sep = "")
      print(message)
    }
  }
  
  print("Done!")
}

if(!interactive()) {
	args <- commandArgs(trailingOnly = TRUE)
  	data_dir <- args[1]
  	output_dir <- args[2]
	main()
}
