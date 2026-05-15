import numpy as np
from collections import deque
from typing import Dict, List, Optional
from app.utils.logger import logger

class AnomalyEngine:
    """
    Engine for real-time statistical anomaly detection using Z-Score.
    Maintains a sliding window of telemetry values for each metric per device.
    """
    def __init__(self, window_size: int = 60, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold
        # Structure: {device_id: {metric_name: deque([values])}}
        self.history: Dict[str, Dict[str, deque]] = {}

    def _update_history(self, device_id: str, metric: str, value: float):
        if device_id not in self.history:
            self.history[device_id] = {}
        if metric not in self.history[device_id]:
            self.history[device_id][metric] = deque(maxlen=self.window_size)
        
        self.history[device_id][metric].append(value)

    def analyze(self, device_id: str, metric: str, value: float) -> Dict:
        """
        Analyzes a new value and returns anomaly details.
        """
        self._update_history(device_id, metric, value)
        
        window = self.history[device_id][metric]
        
        # Need at least a few samples to calculate meaningful stats
        if len(window) < 10:
            return {"is_anomaly": False, "z_score": 0.0, "status": "collecting_data"}

        values = np.array(window)
        mean = np.mean(values)
        std = np.std(values)

        # Handle case where all values are the same (std = 0)
        if std == 0:
            return {"is_anomaly": False, "z_score": 0.0, "status": "stable"}

        z_score = (value - mean) / std
        is_anomaly = abs(z_score) > self.threshold

        if is_anomaly:
            logger.warning(
                f"Anomaly detected for {device_id} - {metric}: "
                f"Value={value}, Mean={mean:.2f}, Z-Score={z_score:.2f}"
            )

        return {
            "is_anomaly": is_anomaly,
            "z_score": float(z_score),
            "mean": float(mean),
            "std": float(std),
            "status": "analyzed"
        }

# Global instance for the app
anomaly_engine = AnomalyEngine(window_size=60, threshold=3.0)
