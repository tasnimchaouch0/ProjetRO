from gurobipy import Model, GRB, quicksum


def build_vrp_model(patients, coords, s, skills_req, agents):
    m = Model("VRP_Model")

    # distances
    d = {}
    for i in patients:
        for j in patients:
            if i != j:
                xi, yi = coords[i]
                xj, yj = coords[j]
                d[i, j] = ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5

    M = 1000

    # Variables
    x = {}
    t = {}

    for k in agents:
        for i, j in d:
            x[i, j, k] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")
        for i in patients:
            t[i, k] = m.addVar(vtype=GRB.CONTINUOUS, name=f"t_{i}_{k}")

    # Compétence
    for j in patients[1:]:
        eligible = [k for k in agents if skills_req[j] in agents[k]["skills"]]
        m.addConstr(quicksum(x[i, j, k] for i in patients if i != j for k in eligible) == 1)

    # Objectif
    m.setObjective(
        quicksum(d[i, j] * x[i, j, k] for i, j in d for k in agents),
        GRB.MINIMIZE,
    )

    # Fenêtres (simplifiées)
    for k in agents:
        for i, j in d:
            m.addConstr(t[j, k] >= t[i, k] + s[i] - M * (1 - x[i, j, k]))

    m.update()
    return m, x, t, d
