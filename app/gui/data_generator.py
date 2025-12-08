# data_generator.py
import random

def generate_random_instance(test_type="small"):
    if test_type == "small":
        num_patients = 5
    elif test_type == "medium":
        num_patients = 8
    elif test_type == "large":
        num_patients = 12
    else:
        num_patients = 5  # fallback

    patients = [0] + list(range(1, num_patients + 1))
    coords = {0: (0, 0)}
    s = {0: 0}
    for i in patients[1:]:
        coords[i] = (random.randint(0, 10), random.randint(0, 10))
        s[i] = random.randint(10, 40)

    # Agents et compétences
    types_soins = ["Nursing", "WoundCare", "Physio"]
    agents = {
        1: {"skills": ["Nursing", "Physio"]},
        2: {"skills": ["Nursing", "WoundCare"]},
    }
    skills_req = {i: random.choice(types_soins) for i in patients[1:]}

    return patients, coords, s, skills_req, agents
