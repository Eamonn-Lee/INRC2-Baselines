from pyomo.environ import *
import sys
from interface import getInstance, milp
instance = milp(getInstance(sys.argv[1]))

# Define the model
model = ConcreteModel()

# Define parameters
nurses = ['Alice', 'Bob', 'Charlie']
days = range(1, 8)  # A one-week period (1 for Monday, 2 for Tuesday, etc.)
shifts = ['Early', 'Day', 'Late', 'Night']
skills = ['HeadNurse', 'Nurse', 'Caretaker', 'Trainee']

# Set of indices
model.N = Set(initialize=nurses)  # Nurses
model.D = Set(initialize=days)    # Days
model.S = Set(initialize=shifts)  # Shifts
model.SK = Set(initialize=skills) # Skills

# Decision variable: x[n,d,s,sk] = 1 if nurse n works shift s on day d with skill sk, else 0
model.x = Var(model.N, model.D, model.S, model.SK, within=Binary)

# Auxiliary slack and excess penalty variables
model.slack = Var(model.D, model.S, model.SK, within=NonNegativeReals)
model.excess_penalty = Var(model.D, model.S, model.SK, within=NonNegativeReals)
model.shift_off_penalty = Var(within=NonNegativeReals)

# Coverage requirements based on the provided specification
min_staffing = {
    ('Early', 'HeadNurse', 1): (1, 1),  # Minimum and optimal coverage for Monday Early HeadNurse
    ('Early', 'Nurse', 1): (1, 1),
    ('Early', 'Caretaker', 1): (2, 3),
    ('Early', 'Trainee', 1): (0, 1),
    # Continue for each shift, skill, and day...
    ('Night', 'Trainee', 7): (1, 1),
}

# Shift-off requests
shift_off_requests = {
    ('CT_18', 'Day', 'Tue'): 1,
    ('CT_27', 'Any', 'Tue'): 1,
    ('HN_3', 'Any', 'Tue'): 1,
    ('HN_3', 'Any', 'Thu'): 1,
    ('NU_14', 'Night', 'Thu'): 1,
    ('TR_36', 'Any', 'Thu'): 1,
    # Continue for all requests as specified...
}

# Minimum staffing requirement with slack
def min_staffing_rule(model, d, s, sk):
    if (s, sk, d) in min_staffing:
        min_req, _ = min_staffing[(s, sk, d)]
        return sum(model.x[n, d, s, sk] for n in model.N) + model.slack[d, s, sk] >= min_req
    return Constraint.Skip
model.min_staffing = Constraint(model.D, model.S, model.SK, rule=min_staffing_rule)

# Optimal staffing requirement with excess penalty
def opt_staffing_rule(model, d, s, sk):
    if (s, sk, d) in min_staffing:
        _, opt_req = min_staffing[(s, sk, d)]
        return sum(model.x[n, d, s, sk] for n in model.N) - model.excess_penalty[d, s, sk] <= opt_req
    return Constraint.Skip
model.opt_staffing = Constraint(model.D, model.S, model.SK, rule=opt_staffing_rule)

# Shift-off requests penalty
def shift_off_request_penalty(model):
    return model.shift_off_penalty >= sum(
        model.x[n, d, s, sk] * shift_off_requests.get((n, s, d), 0)
        for n in model.N for d in model.D for s in model.S for sk in model.SK
    )
model.shift_off_request_penalty = Constraint(rule=shift_off_request_penalty)

# Objective Function: Minimize slack, excess penalties, and shift-off penalties
model.obj = Objective(
    expr=sum(model.slack[d, s, sk] for d in model.D for s in model.S for sk in model.SK) +
         sum(model.excess_penalty[d, s, sk] for d in model.D for s in model.S for sk in model.SK) +
         model.shift_off_penalty,
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
