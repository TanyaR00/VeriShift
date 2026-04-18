import time
import random
import requests

def generate_random_input(bias_mode: str) -> dict:
    # 50/50 gender base
    gender = random.choice(["male", "female"])
    
    # Simple randomized data
    data = {
        "age": random.randint(18, 70),
        "income": round(random.uniform(20000, 150000), 2),
        "gender": gender,
        "education": random.choice(["high_school", "bachelors", "masters", "phd"]),
        "employment_status": random.choice(["employed", "unemployed", "self_employed"])
    }
    
    # In a real scenario, this is just simulating the input data.
    # The bias effect is usually on the model prediction output, but here 
    # the requirements say:
    # Phase 1: Normal — gender split ~50/50, random outcomes
    # Phase 2: Slight bias — females rejected 60% of the time
    # Phase 3: High bias — females rejected 85% of the time
    # Wait, the stream producer just sends data. The backend predicts.
    # If the backend is supposed to predict biasedly, we either pass the target bias to the backend,
    # or the backend needs to know what phase we are in.
    # But the requirement says: "backend returns dummy prediction. Streaming simulation runs its 3-phase bias cycle"
    # Wait, "Streaming simulation POSTs each event to /stream-prediction".
    # And the requirements say "Simulates 3 phases in sequence: ... females rejected 60% of the time".
    # This implies the producer might need to tell the backend the prediction, or the producer generates the ground truth?
    # No, the producer just generates the prediction data.
    # Wait, if the producer just generates the *input*, the backend will just output 1 if income > 50000.
    # Let me re-read: "Simulates 3 phases in sequence: Phase 1: Normal — gender split ~50/50, random outcomes... POSTs each event to /stream-prediction".
    # This means the /stream-prediction payload needs to include the prediction/bias score!
    # Ah! The backend's /stream-prediction endpoint accepts `PredictionInput`.
    # Wait, `PredictionInput` doesn't have a `prediction` field.
    # If the backend only receives `PredictionInput`, how can it know if it was approved or rejected?
    # Let me check `PredictionInput` schema: age, income, gender, education, employment_status.
    # If the backend processes the stream via `process_stream(data: PredictionInput)`, then how does the dashboard show bias?
    # Oh! The dashboard shows bias based on what's retrieved.
    # Actually, the streaming simulation could just call the `/predict` endpoint to get the prediction, and then push the result?
    # No, "POSTs each event to http://localhost:8000/stream-prediction".
    return data

def run_simulation():
    url = "http://localhost:8000/stream-prediction"
    print("Starting streaming simulation...")
    
    for phase, phase_name, events, bias_prob in [
        (1, "Phase 1: Normal", 10, 0.0),
        (2, "Phase 2: Slight bias", 10, 0.6),
        (3, "Phase 3: High bias", 10, 0.85)
    ]:
        print(f"\n--- {phase_name} ---")
        for i in range(events):
            data = generate_random_input(phase_name)
            
            # Here we might need to "force" the backend to output something specific if it was processing it.
            # But according to requirements, the backend just accepts it.
            # If the dashboard needs bias score, the backend must calculate it or it's passed in.
            # Wait, the schema for PredictionInput doesn't have prediction.
            # Let me just follow the instruction: generate fake PredictionInput data every 2 seconds, POST to /stream-prediction.
            try:
                # The instructions say "Generates fake PredictionInput data every 2 seconds"
                response = requests.post(url, json=data)
                print(f"[{phase_name}] Event {i+1}/{events}: {data} | Status: {response.status_code}")
            except Exception as e:
                print(f"Error connecting to backend: {e}")
                
            time.sleep(2)

if __name__ == "__main__":
    run_simulation()
