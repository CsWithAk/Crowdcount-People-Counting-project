# dashboard/data_manager.py
from datetime import datetime
import os
import pandas as pd
import numpy as np

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        self.zone_counts = {}
        self.total_count = 0
        self.history = []
        self.global_threshold = 20  # Default same limit for all zones
        self.heatmap = None
        self.current_frame = None
        self.export_dir = "dashboard/exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def update_counts(self, zone_counts_dict, total):
        self.zone_counts = zone_counts_dict.copy()
        self.total_count = total
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {"time": timestamp, "total": total, "zones": zone_counts_dict.copy()}
        self.history.append(entry)
        if len(self.history) > 500:
            self.history.pop(0)
    
    def update_heatmap(self, heatmap_frame):
        self.heatmap = heatmap_frame.copy()
    
    def set_global_threshold(self, threshold):
        self.global_threshold = int(threshold)
    
    def get_data(self):
        alerts = [zid for zid, count in self.zone_counts.items() if count > self.global_threshold]
        return {
            "total": self.total_count,
            "zones": self.zone_counts,
            "history": self.history[-50:],
            "threshold": self.global_threshold,
            "alerts": alerts
        }
    
    def export_csv(self):
        if not self.history:
            return None
        df = pd.DataFrame(self.history)
        filename = f"crowd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath