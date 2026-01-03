# 🚶 CrowdCount – Real-Time People Counting & Analytics System

**A complete, secure, and professional crowd monitoring system built with Computer Vision, Deep Learning, and Web Dashboard.**

![CrowdCount Registration Form](Register_form.png)  
![CrowdCount Login Form](Login_form.png)
![CrowdCount Admin Dashboard](Admin_dashboard.png)
![CrowdCount User Dashboard](User_dashboard.png)

---

### 🌟 Project Overview

**CrowdCount** is an advanced real-time people counting system that uses **YOLOv8** for detection and **DeepSORT** for tracking. It allows administrators to define custom monitoring zones, view live statistics, receive overcrowding alerts, and export detailed reports.

Perfect for:
- Shopping malls
- Airports & railway stations
- Events & stadiums
- Offices & public spaces
- Security & crowd management

---

### 🎯 Key Features

| Feature                          | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| **Real-Time Detection & Tracking** | YOLOv8 + DeepSORT for accurate person detection with stable unique IDs     |
| **Custom Zone Drawing**          | Draw polygonal zones on video feed using mouse (saved persistently)         |
| **Live Dashboard**               | Beautiful web interface with total count, per-zone counts, charts & heatmap|
| **Line Chart Analytics**         | Time-based crowd trends per zone                                            |
| **Density Heatmap**              | Visual bubble heatmap showing crowd concentration                           |
| **Overcrowding Alerts**          | Beep sound + red alert when any zone exceeds threshold                     |
| **Global Threshold Setting**     | Admin can set same capacity limit for all zones                             |
| **Report Export**                | Export session data in **CSV** and **PDF** format                           |
| **Secure Authentication**        | Login/Register with **Admin** and **User** roles (JWT + cookies)           |
| **Admin Panel**                  | Change camera source (webcam/video), view users, manage system              |
| **Cloud + Local Storage**        | Users stored in **MongoDB Atlas**, zones in local `zones.json`              |
| **Cross-Platform**               | Works on Windows & Linux (CPU-only compatible)                             |

---

### 🛠 Tech Stack

- **Backend**: Python + Flask
- **Computer Vision**: OpenCV
- **Detection**: Ultralytics YOLOv8
- **Tracking**: DeepSORT-Realtime
- **Frontend**: Bootstrap 5 + Chart.js
- **Authentication**: Flask-JWT-Extended
- **Database**: MongoDB Atlas (users) + Local JSON (zones)
- **Reports**: Pandas + ReportLab (PDF)

---

### 📂 Project Structure

Crowdcount-people-counting-project/
-├── milestone_01                     # Project Zone creation
-├── miletone_02                      # People counting deepSORT algorithms Implementation
-├── milestone_03                     # live dashboard and flask app creation
-├── milestone_04                     # Main Internship Project
-    ├── main.py                      # Main Flask app + video processing
-    ├── camera_feed.py               # Camera handling-
-    ├── zones.py                     # Zone management  (local JSON or mongoDB if already zones uploaded)
-    ├── detection/
-    │   ├── detector.py              # YOLOv8 wrapper
-    │   ├── tracker.py               # DeepSORT wrapper
-    │   └── counter.py               # Zone counting + heatmap
-    ├── dashboard/
-    │   ├── /exports/                # CSV & PDF reports
-    │   ├── data_manager.py          # Shared live data
-    │   ├── templates/               # HTML pages (register, login, dashboard)
-    |   |    ├── index.html          # main Admin/User dashboard
-    |   |    ├── login.html          # login form
-    |   |    ├── register.html       # register form
-    |   |    └── static/             # CSS + JS
-    ├── auth/
-    │   └── models.py                # User auth with MongoDB
-    ├── utils/
-    │   └── report_generator.py      # PDF export
-    └── zones.json                   # Saved zones (auto-generated)
 

---

### 🚀 How to Run

#### 1. Clone & Setup
```bash
git clone [https://github.com/CsWithAk/Crowdcount-People-Counting-project.git]
cd crowdcount-project
python -m venv venv
source venv/bin/activate    # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 2. Update MongoDB URL
open auth/modles.py
```bash
MONGODB_URI = "mongodb+srv://youruser:yourpass@yourcluster.mongodb.net/"
```

#### 3. Run this Application
```bash
Python main.py
```

#### 4. Open Our Browser
```bash
Go to: http://127.0.0.1:5000/login
```
Register first user with role = admin
Login → Full dashboard with all features

---

### 🙏 Acknowledgements

- Ultralytics for YOLOv8
- DeepSORT-Realtime team
- Flask & Bootstrap communities
- MongoDB Atlas (free tier)

---
### 👨‍💻 Author
# Amit Kumar
- Infosys springboard 6.0 Internship Project – 2025
- "Turning pixels into insights – one person at a time."

---

- Star this repo if you found it useful! 🌟
- Feel free to fork and enhance it further.
- Thank you for using CrowdCount! 🚀

---



