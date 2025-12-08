import json
import time
from solver import solve_instance

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def test_large_instance_under_2_seconds():
    data = load("data/dataset_large.json")

    start = time.time()
    solve_instance(data)
    end = time.time()

    assert end - start < 2.0, "Le solveur est trop lent (>2s)"
