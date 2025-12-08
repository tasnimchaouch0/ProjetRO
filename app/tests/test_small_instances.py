import json
from solver import solve_instance

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def test_small_instance_simple():
    data = load("data/dataset_small.json")
    result = solve_instance(data)

    # Vérifie qu'au moins 1 patient est fait
    total_visited = sum(len(v["visited_patients"]) for v in result.values())
    assert total_visited >= 1


def test_basic_instance_assignments():
    data = load("data/dataset_basic.json")
    result = solve_instance(data)

    # Vérifie qu'il n'y a pas de patient dupliqué
    visited = []
    for agent in result.values():
        visited.extend(agent["visited_patients"])

    assert len(visited) == len(set(visited)), "Un patient a été visité 2 fois"
