from app.gui.data_generator import generate_instance
from app.core.solver import solve_instance
import json

# Tester avec différents seeds
for seed in [42, 100, 200]:
    print(f"\n{'='*60}")
    print(f"TEST AVEC SEED={seed}")
    print('='*60)
    
    ds = generate_instance(num_patients=3, num_agents=2, seed=seed)
    
    print("\nPATIENTS:")
    for p in ds['patients']:
        print(f"  P{p['id']}: skill={p['required_skill']}, coords=({p['lat']}, {p['lon']})")
    
    print("\nAGENTS:")
    for a in ds['agents']:
        print(f"  {a['name']}: skills={a['skills']}, max_patients={a['max_patients']}")
    
    # Vérifier couverture des compétences
    required_skills = set(p['required_skill'] for p in ds['patients'])
    available_skills = set()
    for a in ds['agents']:
        available_skills.update(a['skills'])
    
    print(f"\nCompétences requises: {required_skills}")
    print(f"Compétences disponibles: {available_skills}")
    
    missing = required_skills - available_skills
    if missing:
        print(f"⚠️  COMPÉTENCES MANQUANTES: {missing}")
    else:
        print("✅ Toutes les compétences sont couvertes")
    
    # Tenter de résoudre
    print("\nRÉSOLUTION...")
    result, coords = solve_instance(data=ds)
    
    if result:
        total_dist = sum(r.get('total_distance', 0) for r in result.values())
        print(f"✅ SOLUTION TROUVÉE - Distance: {total_dist:.2f}")
        for k, v in result.items():
            print(f"  Agent {k}: {v['route']}")
    else:
        print("❌ INFAISABLE")
