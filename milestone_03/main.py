# main.py
import cv2
import threading
import time
import numpy as np
from flask import Flask, render_template, Response, jsonify, send_from_directory, request
from camera_feed import CameraFeed
from zones import ZoneManager
from detection.detector import YOLODetector
from detection.tracker import DeepSortTracker
from detection.counter import ZoneCounter
from dashboard.data_manager import DataManager
import os

app = Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
data_manager = DataManager()
zone_manager = ZoneManager()
detector = YOLODetector()
tracker = DeepSortTracker()
counter = None
# camera = CameraFeed(source=0)
camera = CameraFeed(source="People_crowd.mp4")  # Your video file name

def process_video():
    global counter
    if not camera.start_camera():
        return
    zone_manager.load_zones()
    if zone_manager.zones:
        counter = ZoneCounter(zone_manager.zones)

    while True:
        ret, frame = camera.read_frame()
        if not ret:
            break

        detections = detector.detect(frame)
        tracks = tracker.update(detections, frame)

        if counter:
            counter.update(tracks)
            counts = counter.get_counts()
            total = sum(counts.values())
            data_manager.update_counts(counts, total)
            heatmap_frame = counter.update_heatmap(frame, tracks)
        else:
            heatmap_frame = frame
            total = len(tracks)

        display_frame = zone_manager.draw_zones(heatmap_frame.copy())
        for (l,t,r,b), tid, _ in tracks:
            cv2.rectangle(display_frame, (int(l),int(t)), (int(r),int(b)), (0,255,255), 2)
            cv2.putText(display_frame, f"ID:{tid}", (int(l),int(t)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        _, jpeg = cv2.imencode('.jpg', display_frame)
        data_manager.current_frame = jpeg.tobytes()

    camera.stop_camera()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            frame = getattr(data_manager, 'current_frame', None)
            if frame:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                blank = np.zeros((480,640,3), np.uint8)
                cv2.putText(blank, 'Camera Starting...', (150,240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                _, jpeg = cv2.imencode('.jpg', blank)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(0.1)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def get_data():
    return jsonify(data_manager.get_data())

@app.route('/set_threshold', methods=['POST'])
def set_threshold():
    threshold = request.json.get('threshold', 20)
    data_manager.set_global_threshold(threshold)
    return jsonify({"status": "ok"})

@app.route('/export_csv')
def export_csv():
    path = data_manager.export_csv()
    if path:
        filename = os.path.basename(path)
        return jsonify({"filename": filename})
    return jsonify({"error": "no data"})

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(data_manager.export_dir, filename)

if __name__ == "__main__":
    threading.Thread(target=process_video, daemon=True).start()
    print("Dashboard: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, threaded=True)