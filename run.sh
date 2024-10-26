#!/bin/bash

# List of instances
instances=(
"n030w4_1_6-2-9-1"
"n030w4_1_6-7-5-3"
"n030w8_1_2-7-0-9-3-6-0-6"
"n030w8_1_6-7-5-3-5-6-2-9"
"n040w4_0_2-0-6-1"
"n040w4_2_6-1-0-6"
"n040w8_0_0-6-8-9-2-6-6-4"
"n040w8_2_5-0-4-8-7-1-7-2"
"n050w4_0_0-4-8-7"
"n050w4_0_7-2-7-2"
"n050w8_1_1-7-8-5-7-4-1-8"
"n050w8_1_9-7-5-3-8-8-3-1"
"n060w4_1_6-1-1-5"
"n060w4_1_9-6-3-8"
"n060w8_0_6-2-9-9-0-8-1-3"
"n060w8_2_1-0-3-4-0-3-9-1"
"n080w4_2_4-3-3-3"
"n080w4_2_6-0-4-8"
"n080w8_1_4-4-9-9-3-6-0-5"
"n080w8_2_0-4-0-9-1-9-6-2"
"n100w4_0_1-1-0-8"
"n100w4_2_0-6-4-6"
"n100w8_0_0-1-7-8-9-1-5-4"
"n100w8_1_2-4-7-9-3-9-2-8"
"n120w4_1_4-6-2-6"
"n120w4_1_5-6-9-8"
"n120w8_0_0-9-9-4-5-1-0-3"
"n120w8_1_7-2-6-4-5-2-0-2"
)

testin=(
    "n030w4_1_6-2-9-1"
)

# Directory to store all output files
output_dir="compset_out"

sudo rm -r "$output_dir" 
echo "clearing old"
sleep 2
mkdir -p "$output_dir"
sudo chmod -R 777 "$output_dir"

sudo docker run --rm legraina/nurse-scheduler #Load up the docker idk


# Loop over each instance and run the Docker command
#for instance in "${testin[@]}"; do
for instance in "${instances[@]}"; do
    # Define the output file for each instance
    output_file="$output_dir/${instance}.txt"
    
    # Run the Docker command and save the output to the file
    echo "Running: $instance"
    #wack ass tee workaround
    #add Algo here
    
    
    echo "Output: $output_file"
done

echo "processed"
