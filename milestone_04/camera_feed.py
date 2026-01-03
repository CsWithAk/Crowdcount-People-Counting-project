import cv2
import numpy as np

class CameraFeed:
    def __init__(self, source=0):
        """
        Initialize camera feed
        source: 0 for webcam, 1 for USB camera, or IP camera URL
        """
        self.cap = None
        self.source = source
        self.is_opened = False


     # In camera_feed.py, modify start_camera method
    def start_camera(self):
        try:
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()

            # Use default or FFmpeg if video file
            backend = cv2.CAP_ANY
            if isinstance(self.source, str) and self.source.lower().endswith(('.mp4', '.avi', '.mov')):
                backend = cv2.CAP_FFMPEG

            self.cap = cv2.VideoCapture(self.source, backend)
            if not self.cap.isOpened():
                print(f"Error: Cannot open source {self.source}")
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            self.is_opened = True
            print("Camera started successfully")
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False   
        
    
    def read_frame(self):
        """Read a frame from camera"""
        if not self.is_opened or self.cap is None:
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            print("Can't receive frame. Camera may be disconnected.")
            return False, None
            
        return True, frame
    
    def stop_camera(self):
        """Stop and release camera"""
        if self.cap is not None:
            self.cap.release()
        self.is_opened = False
        cv2.destroyAllWindows()
        print("Camera stopped")
    
    def get_frame_info(self):
        """Get frame width, height and FPS"""
        if not self.is_opened or self.cap is None:
            return 0, 0, 0
            
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        return width, height, fps