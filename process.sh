#!/bin/sh

# Define function to get time in hh:mm:ss format
get_time() {
	(( h=${1}/3600 ))
 	(( m=(${1}%3600)/60 ))
 	(( s=${1}%60 ))
 	time=$(printf "%02d:%02d:%02d\n" $h $m $s)
 	echo "took $time (hh:mm:ss)"
}

# Define variables to be used as arguments
data_dir="/Volumes/LV_HD/Accelerometry/daily_GRF/data/"
base_output_dir="/Volumes/LV_HD/Accelerometry/daily_GRF/output/"
component="resultant"
placement="back"

echo $'Running analysis...\n'
start=$(date +%s)
for d in "${data_dir}"*/; do
	# Define data dir
    data_dir="$d"

    # Define output dir
    suffix="$(echo $data_dir | cut -d '/' -f 7)/"
    output_dir="${base_output_dir}$suffix"
    
	echo Selected directory: $data_dir
	echo
	
	echo $'Part 1: Convert gt3x files into txt'
	echo $'Script part1_gt3x_to_txt.R'
	start1=$(date +%s)
	Rscript code/part1_gt3x_to_txt.R $data_dir $output_dir
	end1=$(date +%s)
	time1=$(( $end1 - $start1 ))
	echo $'\n'
	echo "Part 1 $(get_time $time1)"
	echo $'\n'
	
	echo $'Part 2: Detect and mark wear time'
	echo $'Script part2_mark_wear_time.R'
	start2=$(date +%s)
	Rscript code/part2_mark_wear_time.R  $data_dir $output_dir
	end2=$(date +%s)
	time2=$(( $end2 - $start2 ))
	echo $'\n'
	echo "Part 2 $(get_time $time2)"
	echo $'\n'
	
	echo $'Part 3: Process raw acc...'
	echo $'...extract information from wear time log...'
	echo $'...filter raw accelerometer signal and find acceleration peaks'
	echo $'Script part3_process_raw_acc.py'
	start3=$(date +%s)
	python3 code/part3_process_raw_acc.py $data_dir $output_dir $component
	end3=$(date +%s)
	time3=$(( $end3 - $start3 ))
	echo $'\n'
	echo "Part 3 $(get_time $time3)"
	echo $'\n'
	
	echo $'Part 4: Compute ground reaction forces'
	echo $'Script part4_compute_GRF'
	start4=$(date +%s)
	python3 code/part4_compute_GRF.py $data_dir $output_dir $component $placement
	end4=$(date +%s)
	time4=$(( $end4 - $start4 ))
	echo $'\n'
	echo "Part 4 $(get_time $time4)"
	echo $'\n'
	
	echo $'Part 5: Compute data summaries'
	echo $'Script part5_clean_df'
	start5=$(date +%s)
	Rscript code/part5_clean_df.R $output_dir
	end5=$(date +%s)
	time5=$(( $end5 - $start5 ))
	echo $'\n'
	echo "Part 5 $(get_time $time5)"
	echo $'\n'

	echo $'Analysis finished'
	echo $'\n'

    # Reset output dir 
    output_dir=$base_output_dir
done
end=$(date +%s)
time=$(( $end - $start ))

echo "The whole analysis $(get_time $time)"