from app.core.solver import solve_instance
from app.gui.data_generator import generate_instance


def test_small_instance_simple():
    data = generate_instance(test_type="small", num_patients=6, num_agents=3, seed=1)
    result, _ = solve_instance(data=data)

    total_visited = sum(len(v["visited_patients"]) for v in result.values())
    assert total_visited >= 1


def test_basic_instance_assignments():
    data = generate_instance(test_type="small", num_patients=8, num_agents=4, seed=2)
    result, _ = solve_instance(data=data)

    visited = []
    for agent in result.values():
        visited.extend(agent["visited_patients"])

    assert len(visited) == len(set(visited)), "Un patient a été visité 2 fois"
