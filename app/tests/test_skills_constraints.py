import pytest
import json
from solver import solve_instance

@pytest.mark.skip(reason="Les compétences ne sont pas encore implémentées")
def test_agents_only_visit_compatible_patients():
    data = {
        "agents": [{"id": 1, "skills": ["wound"], "lat": 0, "lon": 0}],
        "patients": [
            {"id": 101, "required_skill": "wound", "lat": 0, "lon": 0, "duration": 10, "time_window": [0, 100]},
            {"id": 102, "required_skill": "pediatrics", "lat": 0, "lon": 0, "duration": 10, "time_window": [0, 100]}
        ]
    }

    result = solve_instance(data)

    # Vérifie qu'aucun patient incompatible n'a été attribué
    for agent_id, r in result.items():
        for p in r["visited_patients"]:
            patient = next(x for x in data["patients"] if x["id"] == p)
            assert patient["required_skill"] in data["agents"][0]["skills"]
