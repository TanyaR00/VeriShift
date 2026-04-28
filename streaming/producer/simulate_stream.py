import requests
import random
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def generate_event(phase: str) -> dict:
    gender = random.choice(["male", "female"])
    
    if phase == "normal":
        if gender == "female":
            prediction = 1 if random.random() > 0.5 else 0
        else:
            prediction = 1 if random.random() > 0.5 else 0
    elif phase == "slight_bias":
        if gender == "female":
            prediction = 1 if random.random() > 0.6 else 0
        else:
            prediction = 1 if random.random() > 0.35 else 0
    else:  # high_bias
        if gender == "female":
            prediction = 1 if random.random() > 0.85 else 0
        else:
            prediction = 1 if random.random() > 0.2 else 0

    return {
        "age": random.randint(22, 60),
        "income": round(random.uniform(20000, 120000), 2),
        "gender": gender,
        "education": random.choice(["high_school", "bachelors", "masters", "phd"]),
        "employment_status": random.choice(["employed", "unemployed", "self_employed"]),
        "prediction": prediction,
        "timestamp": datetime.utcnow().isoformat()
    }

def run():
    phases = [
        ("normal", 10),
        ("slight_bias", 10),
        ("high_bias", 10),
    ]

    print("🚀 VeriShift Streaming Simulation Started")
    print("=" * 50)

    for phase_name, count in phases:
        print(f"\n📊 Phase: {phase_name.upper()}")
        for i in range(count):
            event = generate_event(phase_name)
            try:
                res = requests.post(
                    f"{BASE_URL}/stream-prediction",
                    json=event,
                    timeout=2
                )
                status = "✅" if res.status_code == 200 else "❌"
                print(f"  {status} Event {i+1}/{count} | "
                      f"gender={event['gender']} | "
                      f"prediction={'approved' if event['prediction']==1 else 'rejected'}")
            except Exception as e:
                print(f"  ⚠️  Backend unavailable: {e}")

            time.sleep(2)

    print("\n✅ Simulation complete — all 30 events sent")
    print("Dashboard should show full bias progression")

if __name__ == "__main__":
    run()
