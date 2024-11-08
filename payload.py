import subprocess
import sys

#"n030w4_1_6-2-9-1"
f_in= sys.argv[1]

base_dirr="datasets/INRC2"

instance = f_in.split('_')
dataset = instance[0]
his = instance[1]
order = instance[2].split('-')

sce_file=f"{base_dirr}/{dataset}/Sc-{dataset}.txt"
his_file=f"{base_dirr}/{dataset}/H0-{dataset}-{his}.txt"

week_files = [f"{base_dirr}/{dataset}/WD-{dataset}-{x}.txt" for x in order]

sol=["Sol-n005w4-1-0.txt", "Sol-n005w4-2-1.txt", "Sol-n005w4-3-2.txt", "Sol-n005w4-3-3.txt"]

validate_comm = f"java -jar validator.jar --sce {sce_file} --his {his_file} --weeks {' '.join(week_files)} --sols {' '.join(sol)}"
print(validate_comm)