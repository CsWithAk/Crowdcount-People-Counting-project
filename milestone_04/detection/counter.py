# detection/counter.py
import cv2
import numpy as np

class ZoneCounter:
    def __init__(self, zones):
        self.zones = zones
        self.counted_ids = {zone['id']: set() for zone in zones}
        self.current_counts = {zone['id']: 0 for zone in zones}

    def point_in_polygon(self, point, polygon):
        return cv2.pointPolygonTest(np.array(polygon, np.int32), point, False) >= 0

    def update(self, tracks):
        current_in_zone = {zone['id']: set() for zone in self.zones}

        for ltrb, track_id, _ in tracks:
            left, top, right, bottom = map(int, ltrb)
            centroid = ((left + right) // 2, bottom)

            for zone in self.zones:
                if self.point_in_polygon(centroid, zone['points']):
                    current_in_zone[zone['id']].add(track_id)
                    if track_id not in self.counted_ids[zone['id']]:
                        self.counted_ids[zone['id']].add(track_id)
                        self.current_counts[zone['id']] += 1

    def get_counts(self):
        return self.current_counts.copy()

    def reset(self):
        self.counted_ids = {zone['id']: set() for zone in self.zones}
        self.current_counts = {zone['id']: 0 for zone in self.zones}

    def update_heatmap(self, frame, tracks):
        height, width = frame.shape[:2]
        heat = np.zeros((height, width), dtype=np.float32)

        if len(tracks) == 0:
            overlay = cv2.addWeighted(frame, 0.9, np.full_like(frame, 40), 0.1, 0)
            return overlay

        for ltrb, _, _ in tracks:
            left, top, right, bottom = map(int, ltrb)
            cx, cy = (left + right) // 2, bottom
            cv2.circle(heat, (cx, cy), 35, 1.0, -1)

        heat = cv2.GaussianBlur(heat, (91, 91), 0)

        if heat.max() == 0:
            return frame

        heat_norm = np.uint8(255 * heat / heat.max())
        heatmap_color = cv2.applyColorMap(heat_norm, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(frame, 0.7, heatmap_color, 0.3, 0)
        return overlay