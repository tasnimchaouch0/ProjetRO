from gurobipy import GRB

from ..gui.data_generator import generate_instance
from .model_builder import build_vrp_model
from ..models.domain import VRPInstance


def _build_internal_sets(instance: VRPInstance):
    """Construit les structures internes à partir d'une VRPInstance."""
    depot = instance.depot
    patients_list = instance.patients
    agents_list = instance.agents

    patients = [depot.id] + [p.id for p in patients_list]
    coords = {depot.id: depot.get_coords()}
    service_times = {depot.id: 0}
    skills_req = {}

    for p in patients_list:
        coords[p.id] = p.get_coords()
        service_times[p.id] = p.duration
        skills_req[p.id] = p.required_skill

    # Construire le dict agents avec toutes les propriétés
    agents = {}
    for a in agents_list:
        agents[a.id] = {
            "skills": a.skills,
            "max_patients": a.max_patients,
            "shift_duration": a.shift_duration
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

    Accepts either a VRPInstance object or will generate one based on size parameters.
    Returns a result dict and coords so GUI/tests stay in sync.
    """
    # Valider les limites avant de générer/résoudre
    if num_patients is not None and num_patients > 10:
        raise ValueError("Maximum 10 patients allowed due to license limits")
    if num_agents is not None and num_agents > 10:
        raise ValueError("Maximum 10 agents allowed due to license limits")

    # Si data est un dict (rétrocompatibilité), le convertir en VRPInstance
    if isinstance(data, dict):
        instance = VRPInstance.from_dict(data)
    elif isinstance(data, VRPInstance):
        instance = data
    elif data is None:
        instance = generate_instance(test_type, num_patients, num_agents, seed)
    else:
        instance = data
    
    # Valider la taille de l'instance
    if len(instance.patients) > 10 or len(instance.agents) > 10:
        raise ValueError(f"Instance trop grande: {len(instance.patients)} patients, {len(instance.agents)} agents. Max: 10 patients, 10 agents")

    patients, coords, s, skills_req, agents = _build_internal_sets(instance)

    try:
        m, x, t, d = build_vrp_model(patients, coords, s, skills_req, agents)
        m.optimize()

        if m.status != GRB.OPTIMAL:
            return {}, coords

        routes = _extract_routes(patients, agents, x, coords)
        result = _result_with_distance(routes, coords)
        return result, coords
    except Exception as e:
        print(f"Erreur lors de l'optimisation: {e}")
        return {}, coords
    return result, coords
