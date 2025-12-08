import json
from solver import solve_instance

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def test_medium_has_assignments():
    data = load("data/dataset_medium.json")
    result = solve_instance(data)

    # Il doit y avoir au moins un agent avec > 1 visite
    assert any(len(a["visited_patients"]) >= 1 for a in result.values())


def test_no_overlap_patients():
    data = load("data/dataset_medium.json")
    result = solve_instance(data)

    visits = []
    for r in result.values():
        visits.extend(r["visited_patients"])
    assert len(visits) == len(set(visits)), "Patient visité deux fois"
