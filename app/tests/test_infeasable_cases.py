import json
from solver import solve_instance

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def test_infeasible_keeps_running():
    data = load("data/dataset_edgecases.json")

    result = solve_instance(data)

    # Le solveur doit toujours retourner une structure valide, même si vide
    assert isinstance(result, dict)
    for k, v in result.items():
        assert "visited_patients" in v
        assert isinstance(v["visited_patients"], list)
