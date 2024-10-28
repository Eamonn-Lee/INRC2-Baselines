import os
import re

INRC2_DIR = "datasets/INRC2/"

def week(weekdata, num):
    f =  INRC2_DIR + f"{weekdata}/WD-{weekdata}-{num}.txt"
    if not os.path.exists(f):
        raise Exception(f"Fail to locate Wfile: {f}")
    return f

def history(weekdata, num):
    f =  INRC2_DIR + f"{weekdata}/H0-{weekdata}-{num}.txt"
    if not os.path.exists(f):
        raise Exception(f"Fail to locate Hfile: {f}")
    return f

def scenario(weekdata):
    f =  INRC2_DIR + f"{weekdata}/Sc-{weekdata}.txt"
    if not os.path.exists(f):
        raise Exception(f"Fail to locate Scfile: {f}")
    return f

def getInstance(instance_name):
    #"n040w8_2_5-0-4-8-7-1-7-2"
    instance = {}
    arg = (instance_name).split('_')
    if len(arg) != 3:
        raise Exception("Bad command")

    weeks = arg[2].split('-')

    weekfiles = []
    for num in weeks:
        file_path = f"datasets/INRC2/{str(arg[0])}/{str(week(arg[0], num))}"

        weekfiles.append(file_path)

    instance["weeks"] = weekfiles
    instance["history"] = history(arg[0], arg[1])
    instance["scenario"] = scenario(arg[0])

    print(instance)
    return instance

i = "n040w8_2_5-0-4-8-7-1-7-2"
print(getInstance(i))
        
def milp(instance):
    with open(instance["scenario"], 'r') as f:
        lines = f.readlines
    
    for line in lines:
        line = line.strip()
