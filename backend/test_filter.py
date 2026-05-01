from main import ROBOT_DB, filter_robots_by_requirements

results = filter_robots_by_requirements(5.0, 0.3)
for r in results:
    print(f"{r['id']} ({r['robot_type']}) - payload: {r['max_payload_kg']}kg")

print("\n--- All robots that pass 5kg payload check ---")
for r in ROBOT_DB:
    if 5.0 + 0.3 <= r["max_payload_kg"]:
        print(f"{r['id']}: {r['max_payload_kg']}kg")