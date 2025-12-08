# solver.py
from ..gui.data_generator import generate_random_instance
from .model_builder import build_vrp_model

def solve_instance(test_type="small"):
    # passer le type de test à ton générateur de données
    patients, coords, s, skills_req, agents = generate_random_instance(test_type)

    m, x, t, d = build_vrp_model(patients, coords, s, skills_req, agents)

    m.optimize()

    routes = {}
    if m.status != 2:
        return {}, coords

    for k in agents:
        route = [0]
        current = 0
        visited = set()

        while len(visited) < len(patients) - 1:
            found = False
            for j in patients[1:]:
                if j != current and x[current, j, k].x > 0.5 and j not in visited:
                    route.append(j)
                    visited.add(j)
                    current = j
                    found = True
                    break
            if not found:
                break

        route.append(0)
        routes[k] = route

    return routes, coords
