#!/bin/sh

# Define variables to be used as arguments
data_dir="/Volumes/LVERAS/daily_GRF/data/"
base_output_dir="/Volumes/LVERAS/daily_GRF/output/"

echo $'Running analysis...\n'
for d in "${data_dir}"*/
do
	# Define data dir
    data_dir="$d"

    # Define output dir
    suffix="$(echo $data_dir | cut -d '/' -f 6)/"
    output_dir="${base_output_dir}$suffix"
    
	echo Selected directory: $data_dir
	echo
	
	echo $'Step 1: Convert gt3x files into txt'
	echo $'Script 01_gt3x_to_txt.R\n'
	Rscript code/01_gt3x_to_txt.R $data_dir $output_dir
	echo $'\n'
	
	echo $'Step 2: Detect and mark wear time'
	echo $'Script 02_mark_wear_time.R\n'
	Rscript code/02_mark_wear_time.R  $data_dir $output_dir
	echo $'\n'
	
	echo $'Step 3: Process raw acc...'
	echo $'...extract information from wear time log...'
	echo $'...filter raw accelerometer signal and find acceleration peaks'
	echo $'Script 03_process_raw_acc.py\n'
	python3 code/03_process_raw_acc.py $data_dir $output_dir
	echo $'\n'
	
	echo $'Step 4: Compute ground reaction forces'
	echo $'Script 04_compute_GRF\n'
	python3 code/04_compute_GRF.py $data_dir $output_dir
	echo $'\n'
	
	echo $'Analysis finished'

    # Reset output dir 
    output_dir=$base_output_dir
done