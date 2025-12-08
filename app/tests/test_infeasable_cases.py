from app.core.solver import solve_instance


def test_infeasible_keeps_running():
    # Patient demande une compétence absente des agents
    data = {
        "depot": {"id": 0, "lat": 0, "lon": 0},
        "agents": [
            {"id": 1, "name": "Infirmier 1", "skills": ["Nursing"], "lat": 0, "lon": 0},
        ],
        "patients": [
            {"id": 101, "required_skill": "WoundCare", "lat": 1, "lon": 1, "duration": 10, "time_window": [0, 100]}
        ],
    }

    result, _ = solve_instance(data)

    assert isinstance(result, dict)
    # If infeasible, result can be empty but still dict
    for k, v in result.items():
        assert "visited_patients" in v
        assert isinstance(v["visited_patients"], list)
