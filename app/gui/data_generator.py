import random
from ..models.domain import Patient, Agent, Depot, VRPInstance


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

    Returns a VRPInstance object with agents (infirmiers) and patients, including skills.
    Garantit qu'au moins un agent peut servir chaque patient.
    """
    rand_gen = random.Random(seed)

    if num_patients is None:
        if test_type in ("Random Small", "small"):
            num_patients = 5
        elif test_type in ("Random Medium", "medium"):
            num_patients = 10
        else:
            num_patients = 20

    depot = Depot(id=0, lat=0.0, lon=0.0)

    # Créer les agents d'abord pour connaître les compétences disponibles
    agents = []
    all_available_skills = set()
    
    for aid in range(1, num_agents + 1):
        skills = _pick_agent_skills(rand_gen, aid - 1)
        all_available_skills.update(skills)
        agents.append(
            Agent(
                id=aid,
                name=f"Infirmier {aid}",
                skills=skills,
                lat=depot.lat,
                lon=depot.lon,
                max_patients=rand_gen.randint(4, 8),
                shift_duration=300,
            )
        )
    
    # S'assurer que tous les types de compétences sont couverts
    # Si certaines compétences manquent, les ajouter aux agents existants
    missing_skills = set(SKILL_TYPES) - all_available_skills
    if missing_skills and agents:
        for skill in missing_skills:
            # Ajouter la compétence manquante à un agent aléatoire
            agent_idx = rand_gen.randint(0, len(agents) - 1)
            agents[agent_idx].add_skill(skill)

    # Créer les patients en utilisant uniquement les compétences disponibles
    available_skills_list = list(all_available_skills) if all_available_skills else SKILL_TYPES
    
    patients = []
    for pid in range(1, num_patients + 1):
        duration = rand_gen.randint(10, 40)
        tw_start = rand_gen.randint(0, 60)
        tw_end = tw_start + duration + rand_gen.randint(20, 60)
        
        patients.append(
            Patient(
                id=pid,
                required_skill=rand_gen.choice(available_skills_list),
                lat=rand_gen.randint(0, 10),
                lon=rand_gen.randint(0, 10),
                duration=duration,
                time_window=[tw_start, min(tw_end, 200)],
            )
        )

    return VRPInstance(depot=depot, agents=agents, patients=patients)
