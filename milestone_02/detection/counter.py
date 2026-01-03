# detection/counter.py
import cv2
import numpy as np

class ZoneCounter:
    def __init__(self, zones):
        self.zones = zones  # List from ZoneManager
        self.counted_ids = {zone['id']: set() for zone in zones}
        self.current_counts = {zone['id']: 0 for zone in zones}

    def point_in_polygon(self, point, polygon):
        return cv2.pointPolygonTest(np.array(polygon, np.int32), point, False) >= 0

    def update(self, tracks):
        """
        tracks: list of (ltrb, track_id, class_id)
        Updates counts only when a person enters a zone (centroid crosses in)
        """
        # Reset current frame presence
        current_in_zone = {zone['id']: set() for zone in self.zones}

        for ltrb, track_id, _ in tracks:
            left, top, right, bottom = map(int, ltrb)
            centroid = ((left + right) // 2, (bottom + top) // 2)  # Use bottom center for better entry detection

            for zone in self.zones:
                if self.point_in_polygon(centroid, zone['points']):
                    current_in_zone[zone['id']].add(track_id)
                    # Count only once per person per zone
                    if track_id not in self.counted_ids[zone['id']]:
                        self.counted_ids[zone['id']].add(track_id)
                        self.current_counts[zone['id']] += 1

        # Optional: Remove people who left (uncomment if needed)
        # for zone_id in self.counted_ids:
        #     self.counted_ids[zone_id] -= (self.counted_ids[zone_id] - current_in_zone[zone_id])

    def get_counts(self):
        return self.current_counts.copy()

    def reset(self):
        self.counted_ids = {zone['id']: set() for zone in self.zones}
        self.current_counts = {zone['id']: 0 for zone in self.zones}