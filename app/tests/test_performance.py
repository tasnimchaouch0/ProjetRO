import time

from app.core.solver import solve_instance
from app.gui.data_generator import generate_instance


def test_large_instance_under_2_seconds():
    data = generate_instance(test_type="large", num_patients=20, num_agents=8, seed=4)

    start = time.time()
    solve_instance(data=data)
    end = time.time()

    assert end - start < 2.0, "Le solveur est trop lent (>2s)"
