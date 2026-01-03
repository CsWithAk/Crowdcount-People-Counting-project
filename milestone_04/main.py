# main.py
import cv2
import threading
import time
import numpy as np
import os
from flask import Flask, render_template, Response, jsonify, send_from_directory, request, redirect, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies, get_jwt
)
from camera_feed import CameraFeed
from zones import ZoneManager
from detection.detector import YOLODetector
from detection.tracker import DeepSortTracker
from detection.counter import ZoneCounter
from dashboard.data_manager import DataManager
from auth.models import create_user, verify_user, get_all_users
from utils.report_generator import generate_pdf

app = Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
app.secret_key = 'amitkumar'
app.config['JWT_SECRET_KEY'] = 'amit'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

# Global objects
data_manager = DataManager()
zone_manager = ZoneManager()
detector = YOLODetector()
tracker = DeepSortTracker()
counter = None
camera = None
processing_thread = None

def process_video():
    global counter, camera

    if camera is None or not camera.start_camera():
        print("Failed to start camera in thread")
        return

    # Load zones once at start
    zone_manager.load_zones()
    if zone_manager.zones:
        counter = ZoneCounter(zone_manager.zones)
    else:
        counter = None

    print("Video processing started")

    while True:
        if camera is None or not hasattr(camera, 'is_opened') or not camera.is_opened:
            time.sleep(0.1)
            continue

        ret, frame = camera.read_frame()
        if not ret:
            time.sleep(0.1)
            continue

        # Detection & Tracking
        detections = detector.detect(frame)
        tracks = tracker.update(detections, frame)

        current_counts = {}
        total = 0

        if counter and zone_manager.zones:
            counter.update(tracks)
            current_counts = counter.get_counts()
            total = sum(current_counts.values())
            heatmap_frame = counter.update_heatmap(frame, tracks)
        else:
            heatmap_frame = frame
            total = len(tracks)

        # Update data manager
        data_manager.update_counts(current_counts, total)

        # Draw zones and bounding boxes
        display_frame = zone_manager.draw_zones(heatmap_frame.copy(), show_labels=True)

        for (l, t, r, b), tid, _ in tracks:
            cv2.rectangle(display_frame, (int(l), int(t)), (int(r), int(b)), (0, 255, 255), 2)
            cv2.putText(display_frame, f"ID:{tid}", (int(l), int(t)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Encode for web streaming
        _, jpeg = cv2.imencode('.jpg', display_frame)
        data_manager.current_frame = jpeg.tobytes()

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        success, msg = create_user(username, password, role)
        if success:
            return redirect(url_for('login'))
        return f"<h3 style='color:red'>{msg}</h3><a href='/register'>Try Again</a>"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user(username, password)
        if user:
            access_token = create_access_token(
                identity=username,
                additional_claims={"role": user['role']}
            )
            response = redirect(url_for('index'))
            set_access_cookies(response, access_token)
            return response
        return "<h3 style='color:red'>Invalid credentials</h3><a href='/login'>Try Again</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    unset_jwt_cookies(response)
    return response

@app.route('/')
@jwt_required()
def index():
    username = get_jwt_identity()
    jwt_data = get_jwt()
    role = jwt_data.get('role', 'user')
    return render_template('index.html', role=role, username=username)

@app.route('/video_feed')
@jwt_required()
def video_feed():
    def gen():
        while True:
            frame = getattr(data_manager, 'current_frame', None)
            if frame:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                blank = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(blank, 'Camera Loading...', (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                _, jpeg = cv2.imencode('.jpg', blank)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(0.1)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
@jwt_required()
def get_data():
    return jsonify(data_manager.get_data())

@app.route('/set_threshold', methods=['POST'])
@jwt_required()
def set_threshold():
    jwt_data = get_jwt()
    if jwt_data.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    threshold = request.json.get('threshold', 20)
    data_manager.set_global_threshold(int(threshold))
    return jsonify({"status": "Threshold updated"})

@app.route('/admin/change_camera', methods=['POST'])
@jwt_required()
def change_camera():
    jwt_data = get_jwt()
    if jwt_data.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    global camera, counter, processing_thread

    source_input = request.json.get('source', '0').strip()
    try:
        source = int(source_input)
    except:
        source = source_input

    # Stop old camera and thread
    if camera:
        camera.stop_camera()
        time.sleep(1.0)

    counter = None

    # New camera
    camera = CameraFeed(source=source)

    # Restart processing thread
    if processing_thread and processing_thread.is_alive():
        # Can't stop thread, but we restart it
        pass
    processing_thread = threading.Thread(target=process_video, daemon=True)
    processing_thread.start()

    return jsonify({"status": f"Camera changed to {source}"})

@app.route('/admin/users')
@jwt_required()
def admin_users():
    jwt_data = get_jwt()
    if jwt_data.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    users = []
    for user in get_all_users():
        users.append({
            "username": user['username'],
            "role": user['role'],
            "created_at": str(user.get('created_at', 'N/A'))
        })
    return jsonify(users)

@app.route('/export_csv')
@jwt_required()
def export_csv():
    path = data_manager.export_csv()
    if path:
        return jsonify({"filename": os.path.basename(path)})
    return jsonify({"error": "No data"})

@app.route('/export_pdf')
@jwt_required()
def export_pdf():
    if not data_manager.history:
        return jsonify({"error": "No data"})
    pdf_path = "dashboard/exports/report.pdf"
    generate_pdf(data_manager.history, pdf_path)
    return jsonify({"filename": "report.pdf"})

@app.route('/download/<filename>')
@jwt_required()
def download(filename):
    return send_from_directory("dashboard/exports", filename)

if __name__ == "__main__":
    os.makedirs("dashboard/exports", exist_ok=True)
    # camera = CameraFeed(source=0)    # web cam
    camera = CameraFeed(source="Milestone_03\People_crowd.mp4")    # video source

    processing_thread = threading.Thread(target=process_video, daemon=True)
    processing_thread.start()

    print("=== Crowd Count System - Milestone 4 ===")
    print("Go to http://127.0.0.1:5000/login")
    print("Register an admin account first")
    app.run(host='127.0.0.1', port=5000, threaded=True)
    
    
    
    
    
    
    
    # & E:/infosys/mvenv/Scripts/python.exe e:/infosys/Project/milestone_04/main.py
