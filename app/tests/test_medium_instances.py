from app.core.solver import solve_instance
from app.gui.data_generator import generate_instance


def test_medium_has_assignments():
    data = generate_instance(test_type="medium", num_patients=12, num_agents=5, seed=3)
    result, _ = solve_instance(data=data)

    assert any(len(a["visited_patients"]) >= 1 for a in result.values())


def test_no_overlap_patients():
    data = generate_instance(test_type="medium", num_patients=12, num_agents=5, seed=3)
    result, _ = solve_instance(data=data)

    visits = []
    for r in result.values():
        visits.extend(r["visited_patients"])
    assert len(visits) == len(set(visits)), "Patient visité deux fois"
