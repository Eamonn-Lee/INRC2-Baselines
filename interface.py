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

    return instance

def nurseInfo(n_str):
    #HN_0 PartTime 2 HeadNurse Nurse
    s = n_str.split()
    n = {}

    n["name"] = s[0].strip()
    n["contract"] = s[1].strip()
    n["skills"] = [s[3 + i].strip() for i in range(int(s[2]))]

    return n

def shiftStaffing(s_list):
    shifts = {}
    for s_str in s_list:
        s = s_str.split()
        vals = s[1].strip("()").split(',')

        shifts[s[0].strip()] = tuple(int(v) for v in vals)

    return shifts

def allowedShiftModel(flist, shifts):   #CURSED
    
    forbidden = {}
    for type in shifts:
        forbidden[type] = shifts.copy() #ensure copy

    for req in flist:
        r = req.split()
        shift = r[0].strip()    #subject of forbidden-ness
        n_forbid = int(r[1].strip())    #num of forbidden attached

        if n_forbid > 0:
            for i in range(n_forbid):
                forbidden[shift].remove(r[2+i].strip()) #HELP

    return forbidden

def week_req(line):
    #shifttype role 7 * (minimum, optimal)
    min_staffing = {}

    parts = line.split()
    stype = parts[0].strip()
    role = parts[1].strip()
    requirements = parts[2:]

    for day in range(1, 8):
        min_opt_tuple = tuple(map(int, requirements[day - 1].strip('()').split(',')))
        min_staffing[(stype, role, day)] = min_opt_tuple
    
    return min_staffing


        
def milp(instance):

#import sys
#from interface import getInstance,milp
#instance = milp(getInstance(sys.argv[1]))

    #must be guaranteed that Sc file consistent
    with open(instance["scenario"], 'r') as f:
        lines = f.readlines()
    

    #SCENARIO -----------------
    i = 0
    while i < len(lines):
        line = lines[i].strip()
    
        if line.startswith("WEEKS"):
            n_weeks = line.split('=')[1].strip() #grab second expr
        elif line.startswith("SKILLS"):
            n_skills= int(line.split('=')[1].strip())
            skills = [lines[i+j+1].strip() for j in range(n_skills)] #iterate over amount of skills

        elif line.startswith("SHIFT_TYPES"):
            n_shift_types = int(line.split('=')[1].strip())
            st_lines = [lines[i+j+1].strip() for j in range(n_shift_types)]

            shift_types = shiftStaffing(st_lines) #iterate over amount of shifttypes

        elif line.startswith("FORBIDDEN_SHIFT_TYPES_SUCCESSIONS"):
            shift_sequences = allowedShiftModel([lines[i+j+1].strip() for j in range(len(shift_types))], list(shift_types.keys()))

        elif line.startswith("CONTRACTS"):
            count = int(line.split('=')[1].strip())
            contracts = [lines[i+j+1].strip() for j in range(count)]
        
        elif line.startswith("NURSES"):
            count = int(line.split('=')[1].strip())
            nurses = [nurseInfo(lines[i+j+1].strip()) for j in range(count)] #iterate over amount of shifttypes

        i+=1

    #weeks -----------------
    for week in instance["weeks"]:
        with open(week, 'r') as f:
            lines = f.readlines()
        expected_entries = n_skills * n_shift_types

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("REQUIREMENTS"):
                week_shifts = [lines[i+j+1].strip() for j in range(expected_entries)]

            elif line.startswith("SHIFT_OFF_REQUESTS"):
                n_off = int(line.split('=')[1].strip())
                shift_off = [lines[i+j+1].strip() for j in range(n_off)]


    sc = {
        "days" : 28 if (n_weeks == "4") else 56,
        "skills" : skills,
        "shifts" : shift_types, #not sure
        "shift_seq": shift_sequences,
        "nurse" : nurses
    }
    
    print(sc)

    return sc


