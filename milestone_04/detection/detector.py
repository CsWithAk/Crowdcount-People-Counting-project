# detection/detector.py
from ultralytics import YOLO
import torch

class YOLODetector:
    def __init__(self, model_name="yolov8n.pt", conf_threshold=0.5):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading YOLOv8 on {self.device}")
        self.model = YOLO(model_name)
        self.model.to(self.device)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        """
        Returns list of detections: [x1, y1, x2, y2, confidence, class_id]
        Only person class (class 0)
        """
        results = self.model(frame, conf=self.conf_threshold, classes=[0], verbose=False)[0]
        detections = []
        for box in results.boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            detections.append(list(xyxy) + [conf, 0])  # [x1,y1,x2,y2,conf,class]
        return detections