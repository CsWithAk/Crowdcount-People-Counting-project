# zones.py
import cv2
import numpy as np
import json
import os
from datetime import datetime

ZONES_FILE = "zones.json"  # Local file in project folder

class ZoneManager:
    def __init__(self):
        self.zones = []
        self.drawing = False
        self.current_points = []
        self.selected_zone_id = -1
        self.editing_mode = False
        self.preview_points = []
        self.zone_colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255)
        ]

    def load_zones(self):
        """Load zones from local zones.json file"""
        if os.path.exists(ZONES_FILE):
            try:
                with open(ZONES_FILE, 'r') as f:
                    data = json.load(f)
                    self.zones = data.get('zones', [])
                print(f"Loaded {len(self.zones)} zones from local {ZONES_FILE}")
            except Exception as e:
                print(f"Error loading zones: {e}")
                self.zones = []
        else:
            print("No zones.json found. Starting with empty zones.")
            self.zones = []

    def save_zones(self):
        """Save zones to local zones.json file"""
        try:
            data = {"zones": self.zones}
            with open(ZONES_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved {len(self.zones)} zones to local {ZONES_FILE}")
        except Exception as e:
            print(f"Error saving zones: {e}")

    def draw_zones(self, frame, show_labels=True):
        """Draw all saved zones on the frame"""
        overlay = frame.copy()

        for zone in self.zones:
            points = np.array(zone['points'], np.int32)
            points = points.reshape((-1, 1, 2))
            color = zone.get('color', (0, 255, 0))

            # Draw semi-transparent fill
            cv2.fillPoly(overlay, [points], color)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

            # Draw outline
            cv2.polylines(frame, [points], True, color, 3)

            # Draw label
            if show_labels and len(points) > 0:
                M = cv2.moments(points)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    label = zone.get('name', f"Zone {zone['id']}")
                    cv2.putText(frame, label, (cx - 40, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Draw current drawing preview
        if self.drawing and len(self.current_points) > 0:
            preview_pts = np.array(self.current_points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [preview_pts], False, (255, 255, 255), 2)
            for i, pt in enumerate(self.current_points):
                cv2.circle(frame, pt, 6, (255, 255, 255), -1)
                cv2.putText(frame, str(i+1), (pt[0]+10, pt[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        return frame

    # Keep your existing mouse/drawing methods if you want interactive drawing
    # Or remove them if you only want pre-defined zones