# main.py
import cv2
import numpy as np
from camera_feed import CameraFeed
from zones import ZoneManager
from detection.detector import YOLODetector
from detection.tracker import DeepSortTracker
from detection.counter import ZoneCounter

class CrowdCountApp:
    def __init__(self):
        self.camera = CameraFeed(source=0)  # Change to video path or IP URL if needed
        self.zone_manager = ZoneManager()
        self.detector = YOLODetector(conf_threshold=0.5)
        self.tracker = DeepSortTracker()
        self.zone_counter = None  # Will be initialized after zones load
        self.current_frame = None
        self.mode = "view"
        self.show_info = True
        self.show_boxes = True

    def setup_mouse_callbacks(self):
        cv2.namedWindow('Crowd Count - Milestone 2')
        cv2.setMouseCallback('Crowd Count - Milestone 2', self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == "draw":
                self.zone_manager.start_drawing(x, y)
            elif self.mode == "edit":
                self.zone_manager.select_zone(x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mode == "draw" and self.zone_manager.drawing:
                self.zone_manager.add_point(x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            if self.mode == "draw" and self.zone_manager.drawing:
                self.zone_manager.finish_drawing(x, y)
                self.zone_manager.save_zones()
                self.update_counter()

    def update_counter(self):
        if len(self.zone_manager.zones) > 0:
            self.zone_counter = ZoneCounter(self.zone_manager.zones)
        else:
            self.zone_counter = None

    def add_frame_info(self, frame):
        if not self.show_info:
            return frame

        counts = self.zone_counter.get_counts() if self.zone_counter else {}
        total = sum(counts.values())

        info_text = [
            f"Mode: {self.mode.upper()} | Total People: {total}",
            f"Zones: {self.zone_manager.get_zone_count()} | Selected: {self.zone_manager.selected_zone_id if self.zone_manager.selected_zone_id != -1 else 'None'}",
        ] + [f"{z['name']}: {counts.get(z['id'], 0)}" for z in self.zone_manager.zones]

        info_text += [
            "",
            "D-Draw | E-Edit | V-View | B-Toggle Boxes",
            "S-Save | C-Clear | R-Reset Count | Q-Quit"
        ]

        y_offset = 30
        for i, text in enumerate(info_text):
            color = (0, 255, 255) if i < 2 else (200, 200, 255)
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 30

        return frame

    def handle_keypress(self, key):
        if key == ord('d'):
            self.mode = "draw"
        elif key == ord('e'):
            self.mode = "edit"
        elif key == ord('v'):
            self.mode = "view"
        elif key == ord('s'):
            self.zone_manager.save_zones()
        elif key == ord('c'):
            self.zone_manager.clear_all_zones()
            self.zone_manager.save_zones()
            self.update_counter()
        elif key == ord('r'):
            if self.zone_counter:
                self.zone_counter.reset()
                print("Counts reset!")
        elif key == ord('b'):
            self.show_boxes = not self.show_boxes
        elif key == ord('i'):
            self.show_info = not self.show_info

        return key != ord('q')

    def run(self):
        print("=== CROWD COUNT - MILESTONE 2 (YOLOv8 + DeepSORT) ===")
        if not self.camera.start_camera():
            return

        self.zone_manager.load_zones()
        self.update_counter()

        self.setup_mouse_callbacks()

        while True:
            ret, frame = self.camera.read_frame()
            if not ret:
                break

            self.current_frame = frame.copy()

            # Detection
            detections = self.detector.detect(frame)

            # Tracking
            tracks = self.tracker.update(detections, frame)

            # Zone counting
            if self.zone_counter:
                self.zone_counter.update(tracks)

            # Draw zones
            display_frame = self.zone_manager.draw_zones(frame.copy())

            # Draw tracking boxes and IDs
            if self.show_boxes:
                for (left, top, right, bottom), track_id, _ in tracks:
                    color = (0, 255, 255)  # Yellow
                    cv2.rectangle(display_frame, (int(left), int(top)), (int(right), int(bottom)), color, 2)
                    cv2.putText(display_frame, f"ID: {track_id}", (int(left), int(top)-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Overlay info
            display_frame = self.add_frame_info(display_frame)

            cv2.imshow('Crowd Count - Milestone 2', display_frame)

            if not self.handle_keypress(cv2.waitKey(1) & 0xFF):
                break

        self.zone_manager.save_zones()
        self.camera.stop_camera()
        print("Milestone 2 Completed!")

if __name__ == "__main__":
    app = CrowdCountApp()
    app.run()