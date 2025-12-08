import random


SKILL_TYPES = [
    "Nursing",
    "WoundCare",
    "Pediatrics",
    "Diabetes",
    "Physio",
]


def _pick_agent_skills(rand_gen, idx):
    """Create a richer skill mix for nurses.

    We ensure diversity by forcing a primary speciality per agent and
    optionally adding a secondary skill.
    """
    primary = SKILL_TYPES[idx % len(SKILL_TYPES)]
    secondary_pool = [s for s in SKILL_TYPES if s != primary]
    secondary = rand_gen.sample(secondary_pool, k=1 if rand_gen.random() > 0.4 else 0)
    return sorted({primary, *secondary})


def generate_instance(test_type="Random Small", num_patients=None, num_agents=3, seed=None):
    """Build a reproducible rich dataset used by both GUI and tests.

    Returns a dict with agents (infirmiers) and patients, including skills.
    """
    rand_gen = random.Random(seed)

    if num_patients is None:
        if test_type in ("Random Small", "small"):
            num_patients = 5
        elif test_type in ("Random Medium", "medium"):
            num_patients = 10
        else:
            num_patients = 20

    depot = {"id": 0, "lat": 0.0, "lon": 0.0}

    patients = []
    for pid in range(1, num_patients + 1):
        patients.append(
            {
                "id": pid,
                "required_skill": rand_gen.choice(SKILL_TYPES),
                "lat": rand_gen.randint(0, 10),
                "lon": rand_gen.randint(0, 10),
                "duration": rand_gen.randint(10, 40),
                "time_window": [0, 100],
            }
        )

    agents = []
    for aid in range(1, num_agents + 1):
        agents.append(
            {
                "id": aid,
                "name": f"Infirmier {aid}",
                "skills": _pick_agent_skills(rand_gen, aid - 1),
                "lat": depot["lat"],
                "lon": depot["lon"],
            }
        )

    return {"depot": depot, "agents": agents, "patients": patients}
