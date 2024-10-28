from pyomo.environ import *
import re
from interface import getInstance, milp
import sys

instance = milp(getInstance(sys.argv[1]))
print(instance)



# Define the model
model = ConcreteModel()

# Define parameters
nurses = ['Alice', 'Bob', 'Charlie']
days = range(1, 8)  # A one-week period
shifts = ['Morning', 'Evening', 'Night']
skills = ['HeadNurse', 'Nurse']

# Set of indices
model.N = Set(initialize=nurses)  # Nurses
model.D = Set(initialize=days)    # Days
model.S = Set(initialize=shifts)  # Shifts
model.SK = Set(initialize=skills) # Skills

# Decision variable: x[n,d,s,sk] = 1 if nurse n works shift s on day d with skill sk, else 0
model.x = Var(model.N, model.D, model.S, model.SK, within=Binary)

# Auxiliary slack variables to represent unmet staffing requirements
model.slack = Var(model.D, model.S, model.SK, within=NonNegativeReals)

# Parameters: staffing requirements, nurse skills, preferences
min_staffing = {
    (1, 'Morning', 'HeadNurse'): 1,
    (1, 'Morning', 'Nurse'): 2,
    # Extend this for all days and shifts...
}
nurse_skills = {
    'Alice': ['HeadNurse', 'Nurse'],
    'Bob': ['Nurse'],
    'Charlie': ['Nurse'],
}
preferences = {('Alice', 1, 'Morning'): 1}  # Example preference to avoid working a specific shift

# Define shift_sequences as a parameter
shift_sequences_data = {
    ('Morning', 'Evening'): 1,
    ('Morning', 'Night'): 1,
    ('Evening', 'Morning'): 1,
    ('Night', 'Morning'): 1,
}
model.shift_sequences = Param(model.S, model.S, initialize=shift_sequences_data, default=0)

# Skill Constraint: Only assign skills a nurse has
def skill_constraint(model, n, d, s, sk):
    if sk not in nurse_skills[n]:
        return model.x[n, d, s, sk] == 0
    return Constraint.Skip
model.skill_constraint = Constraint(model.N, model.D, model.S, model.SK, rule=skill_constraint)

# Single Assignment Per Day
def single_assignment_rule(model, n, d):
    return sum(model.x[n, d, s, sk] for s in model.S for sk in model.SK) <= 1
model.single_assignment = Constraint(model.N, model.D, rule=single_assignment_rule)

# Staffing Requirement with Slack
def staffing_rule(model, d, s, sk):
    if (d, s, sk) in min_staffing:
        return sum(model.x[n, d, s, sk] for n in model.N) + model.slack[d, s, sk] >= min_staffing[d, s, sk]
    return Constraint.Skip
model.staffing = Constraint(model.D, model.S, model.SK, rule=staffing_rule)

# Shift Type Successions: Enforce allowed shift sequences
def shift_succession_rule(model, n, d, s1, s2):
    if model.shift_sequences[s1, s2] == 0:
        if d < max(days):  # Ensure it's within the range of days
            return model.x[n, d, s1, 'Nurse'] + model.x[n, d + 1, s2, 'Nurse'] <= 1
    return Constraint.Skip
model.shift_succession = Constraint(model.N, model.D, model.S, model.S, rule=shift_succession_rule)

# Consecutive Assignments: Max consecutive working days
max_consecutive_work = 5  # Set based on INRC-II requirements
def consecutive_work_rule(model, n, d):
    if d <= len(days) - max_consecutive_work:
        return sum(model.x[n, d + i, s, 'Nurse'] for i in range(max_consecutive_work) for s in model.S) <= max_consecutive_work
    return Constraint.Skip
model.consecutive_work = Constraint(model.N, model.D, rule=consecutive_work_rule)

# Consecutive Days Off: Minimum number of days off after max working days
min_days_off = 2
def consecutive_days_off_rule(model, n, d):
    if d <= len(days) - min_days_off:
        return sum(1 - sum(model.x[n, d + i, s, 'Nurse'] for s in model.S) for i in range(min_days_off)) >= min_days_off
    return Constraint.Skip
model.consecutive_days_off = Constraint(model.N, model.D, rule=consecutive_days_off_rule)

# Preferences: Penalize unwanted assignments
model.pref_penalty = Var(within=NonNegativeReals)
def preferences_rule(model):
    return model.pref_penalty >= sum(model.x[n, d, s, 'Nurse'] * preferences.get((n, d, s), 0) for n in model.N for d in model.D for s in model.S)
model.preferences = Constraint(rule=preferences_rule)

# Complete Weekend: Either work both days or none in a weekend
def complete_weekend_rule_1(model, n):
    # Ensure that if a nurse works Saturday, they must also work Sunday
    return model.x[n, 6, 'Morning', 'Nurse'] <= model.x[n, 7, 'Morning', 'Nurse']

def complete_weekend_rule_2(model, n):
    # Ensure that if a nurse works Sunday, they must also work Saturday
    return model.x[n, 7, 'Morning', 'Nurse'] <= model.x[n, 6, 'Morning', 'Nurse']

# Add these two constraints to enforce the complete weekend requirement
model.complete_weekend_1 = Constraint(model.N, rule=complete_weekend_rule_1)
model.complete_weekend_2 = Constraint(model.N, rule=complete_weekend_rule_2)

# Objective: Minimize slack and preferences penalty
model.obj = Objective(
    expr=sum(model.slack[d, s, sk] for d in model.D for s in model.S for sk in model.SK) + model.pref_penalty,
    sense=minimize
)

# Solve the model
solver = SolverFactory('cbc')
result = solver.solve(model, tee=True)  # tee=True to display solver output

# Check if an optimal solution was found
if result.solver.termination_condition == TerminationCondition.optimal:
    print("Optimal solution found")
elif result.solver.termination_condition == TerminationCondition.infeasible:
    print("No feasible solution found")

# Display the results
for n in model.N:
    for d in model.D:
        for s in model.S:
            for sk in model.SK:
                if model.x[n, d, s, sk].value == 1:
                    print(f"Nurse {n} works {s} shift on day {d} with skill {sk}")
