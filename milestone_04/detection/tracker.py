# detection/tracker.py
from deep_sort_realtime.deepsort_tracker import DeepSort

class DeepSortTracker:
    def __init__(self, max_age=30, nn_budget=100):
        self.tracker = DeepSort(
            max_age=max_age,
            nn_budget=nn_budget,
            embedder="mobilenet",
            half=False,  # Disable half precision for CPU compatibility
            bgr=True
        )

    def update(self, detections, frame):
        """
        detections: list of [x1, y1, x2, y2, conf, class_id]
        Returns: list of (ltrb, track_id, class_id)
        """
        formatted_dets = []
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            l, t, w, h = x1, y1, (x2 - x1), (y2 - y1)
            formatted_dets.append(([l, t, w, h], conf, int(cls)))

        tracks = self.tracker.update_tracks(formatted_dets, frame=frame)
        
        active_tracks = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()  # left, top, right, bottom
            active_tracks.append((ltrb, track_id, 0))  # 0 = person class

        return active_tracks