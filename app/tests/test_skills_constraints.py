from app.core.solver import solve_instance


def test_agents_only_visit_compatible_patients():
    data = {
        "depot": {"id": 0, "lat": 0, "lon": 0},
        "agents": [
            {"id": 1, "name": "Infirmier A", "skills": ["WoundCare"], "lat": 0, "lon": 0},
            {"id": 2, "name": "Infirmier B", "skills": ["Pediatrics"], "lat": 0, "lon": 0},
        ],
        "patients": [
            {"id": 101, "required_skill": "WoundCare", "lat": 0, "lon": 0, "duration": 10, "time_window": [0, 100]},
            {"id": 102, "required_skill": "Pediatrics", "lat": 1, "lon": 1, "duration": 10, "time_window": [0, 100]},
        ],
    }

    result, _ = solve_instance(data)

    for agent_id, r in result.items():
        agent = next(a for a in data["agents"] if a["id"] == agent_id)
        for p in r["visited_patients"]:
            patient = next(x for x in data["patients"] if x["id"] == p)
            assert patient["required_skill"] in agent["skills"]
