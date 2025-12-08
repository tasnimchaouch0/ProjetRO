from gurobipy import Model, GRB, quicksum


def build_vrp_model(patients, coords, s, skills_req, agents):
    m = Model("VRP_Model")

    # Calculer les distances euclidiennes
    d = {}
    for i in patients:
        for j in patients:
            if i != j:
                xi, yi = coords[i]
                xj, yj = coords[j]
                d[i, j] = ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5

    M = 1000  # Big-M pour contraintes logiques

    # ==================== VARIABLES ====================
    # x[i,j,k] = 1 si l'agent k va de i à j
    x = {}
    for k in agents:
        for i, j in d:
            x[i, j, k] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")
    
    # t[i,k] = temps d'arrivée de l'agent k au noeud i
    t = {}
    for k in agents:
        for i in patients:
            t[i, k] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_{i}_{k}")

    m.update()

    # ==================== CONTRAINTES ====================
    
    # 1. CONTRAINTE D'AFFECTATION : Chaque patient visité exactement 1 fois par un agent compétent
    for j in patients[1:]:
        eligible = [k for k in agents if skills_req[j] in agents[k]["skills"]]
        if eligible:
            m.addConstr(
                quicksum(x[i, j, k] for i in patients if i != j for k in eligible) == 1,
                name=f"visit_patient_{j}"
            )

    # 2. CONSERVATION DE FLUX : Ce qui entre = ce qui sort pour chaque agent et noeud
    for k in agents:
        for j in patients[1:]:  # Seulement pour les patients, pas le dépôt
            m.addConstr(
                quicksum(x[i, j, k] for i in patients if i != j) == 
                quicksum(x[j, i, k] for i in patients if i != j),
                name=f"flow_conservation_{k}_{j}"
            )

    # 3. DÉPART ET RETOUR AU DÉPÔT : Chaque agent peut partir du dépôt et y retourner
    for k in agents:
        # Si on part, on doit revenir
        m.addConstr(
            quicksum(x[0, j, k] for j in patients[1:]) == 
            quicksum(x[j, 0, k] for j in patients[1:]),
            name=f"depart_retour_{k}"
        )

    # 4. ÉLIMINATION DE SOUS-TOURS (MTZ - Miller-Tucker-Zemlin)
    # Si agent k va de i à j, alors t[j,k] >= t[i,k] + s[i] + temps_trajet
    for k in agents:
        for i in patients:
            for j in patients[1:]:  # Seulement vers les patients, pas vers le dépôt
                if i != j and (i, j) in d:
                    travel_time = d[i, j]
                    m.addConstr(
                        t[j, k] >= t[i, k] + s[i] + travel_time - M * (1 - x[i, j, k]),
                        name=f"mtz_{k}_{i}_{j}"
                    )

    # 5. FENÊTRES TEMPORELLES : Respect des time windows des patients
    # Note: s contient les durées de service, on doit recevoir les fenêtres depuis solver
    for k in agents:
        # Dépôt : temps initial = 0
        m.addConstr(t[0, k] == 0, name=f"depot_time_{k}")
        
        # Patients : arrivée dans une fenêtre raisonnable (simplifiée)
        for j in patients[1:]:
            # Contrainte souple : on peut arriver jusqu'à 300 unités de temps
            m.addConstr(t[j, k] <= 300, name=f"time_window_end_{k}_{j}")

    # 6. CAPACITÉ DES AGENTS : Nombre maximum de patients par agent
    for k in agents:
        max_capacity = agents[k].get("max_patients", len(patients))
        m.addConstr(
            quicksum(x[i, j, k] for i in patients for j in patients[1:] if i != j) <= max_capacity,
            name=f"capacity_{k}"
        )

    # 7. DURÉE MAXIMALE DU SHIFT : Temps total de la tournée
    for k in agents:
        shift_max = agents[k].get("shift_duration", 300)
        # Le temps de retour au dépôt doit respecter le shift max
        m.addConstr(
            t[0, k] <= shift_max,
            name=f"shift_duration_{k}"
        )

    # ==================== FONCTION OBJECTIF ====================
    # Minimiser la distance totale parcourue par tous les agents
    m.setObjective(
        quicksum(d[i, j] * x[i, j, k] for i, j in d for k in agents),
        GRB.MINIMIZE
    )

    m.update()
    return m, x, t, d
