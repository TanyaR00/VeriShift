# VeriShift

VeriShift is an AI fairness auditing platform. This is a project scaffold containing a Flutter frontend and a FastAPI backend with simulated real-time streaming capability.

## Architecture Overview
The system consists of two primary layers:
1. **TwinExplain**: A feature that enables comparing an original prediction with an "alternate reality" (twin) where one feature is artificially manipulated.
2. **Live Tracking**: A live dashboard to track bias trends through real-time streaming simulation.

## Folder Structure
- `frontend/`: Flutter app with UI screens.
- `backend/`: FastAPI backend with core routes and mocked logic.
- `ml_engine/`: Placeholder for the actual Machine Learning logic (handled separately).
- `streaming/`: Contains scripts to simulate incoming streams and process them.
- `shared/`: Pydantic schemas shared across the application.

## How to Run

### Backend (FastAPI)
From the root directory:
```bash
uvicorn backend.main:app --reload
```

### Frontend (Flutter)
From the `frontend/` directory:
```bash
flutter run -d chrome
```

### Streaming Simulation
From the root directory:
```bash
python streaming/producer/simulate_stream.py
```
