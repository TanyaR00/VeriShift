import pandas as pd

class AppState:
    """Simple in-memory singleton to share active dataset and metrics."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.active_dataset = None
            cls._instance.metrics = {
                "bias_score": 0.0,
                "affected_group": "unknown",
                "missing_percentage": 0.0,
                "sensitive_attributes": []
            }
            cls._instance.streaming_history = []
        return cls._instance

# Global singleton instance
state = AppState()
