from app.gui.data_generator import generate_instance
from app.core.solver import solve_instance

print("Test de faisabilite - Seed 42")
print("-" * 50)

ds = generate_instance(num_patients=5, num_agents=2, seed=42)

print("PATIENTS:")
for p in ds['patients']:
    print(f"  P{p['id']}: {p['required_skill']}")

print("\nAGENTS:")
for a in ds['agents']:
    print(f"  {a['name']}: {a['skills']}")

print("\nResolution...")
result, coords = solve_instance(data=ds)

if result:
    total = sum(r.get('total_distance', 0) for r in result.values())
    print(f"\nSOLUTION - Distance: {total:.2f}")
    for k, v in result.items():
        print(f"  Agent {k}: route={v['route']}, patients={v['visited_patients']}")
else:
    print("\nINFAISABLE")
