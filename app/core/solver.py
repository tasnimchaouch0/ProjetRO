from gurobipy import GRB

from ..gui.data_generator import generate_instance
from .model_builder import build_vrp_model


def _build_internal_sets(dataset):
    depot = dataset.get("depot", {"id": 0, "lat": 0.0, "lon": 0.0})
    patients_list = dataset.get("patients", [])
    agents_list = dataset.get("agents", [])

    patients = [depot.get("id", 0)] + [p["id"] for p in patients_list]
    coords = {depot.get("id", 0): (depot.get("lat", 0.0), depot.get("lon", 0.0))}
    service_times = {depot.get("id", 0): 0}
    skills_req = {}

    for p in patients_list:
        coords[p["id"]] = (p["lat"], p["lon"])
        service_times[p["id"]] = p.get("duration", 0)
        skills_req[p["id"]] = p.get("required_skill", "")

    # Construire le dict agents avec toutes les propriétés
    agents = {}
    for a in agents_list:
        agents[a["id"]] = {
            "skills": a.get("skills", []),
            "max_patients": a.get("max_patients", len(patients_list)),
            "shift_duration": a.get("shift_duration", 200)
        }
    
    return patients, coords, service_times, skills_req, agents


def _extract_routes(patients, agents, x, coords):
    routes = {}
    for k in agents:
        route = [0]
        current = 0
        visited = set()

        while len(visited) < len(patients) - 1:
            next_node = None
            for j in patients[1:]:
                if j == current or j in visited:
                    continue
                if x[current, j, k].X > 0.5:
                    next_node = j
                    break
            if next_node is None:
                break
            route.append(next_node)
            visited.add(next_node)
            current = next_node

        route.append(0)
        routes[k] = route
    return routes


def _result_with_distance(routes, coords):
    result = {}
    for aid, route in routes.items():
        total = 0.0
        for i in range(len(route) - 1):
            x1, y1 = coords[route[i]]
            x2, y2 = coords[route[i + 1]]
            total += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        result[aid] = {
            "route": route,
            "visited_patients": [pid for pid in route if pid != 0],
            "total_distance": total,
        }
    return result


def solve_instance(data=None, test_type="Random Small", num_patients=None, num_agents=3, seed=None):
    """Solve VRP instance.

    Accepts either a fully specified dataset (agents/patients/depot) or will
    generate one based on size parameters. Returns a result dict and coords
    so GUI/tests stay in sync.
    """

    dataset = data if data is not None else generate_instance(test_type, num_patients, num_agents, seed)
    patients, coords, s, skills_req, agents = _build_internal_sets(dataset)

    m, x, t, d = build_vrp_model(patients, coords, s, skills_req, agents)
    m.optimize()

    if m.status != GRB.OPTIMAL:
        return {}, coords

    routes = _extract_routes(patients, agents, x, coords)
    result = _result_with_distance(routes, coords)
    return result, coords
