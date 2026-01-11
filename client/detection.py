"""Vehicle detection for client"""
import config
import numpy as np
from ultralytics import YOLO

coco_model = None

def initialize_coco_model():
    """Initialize YOLO model"""
    global coco_model
    
    if config.VERBOSE:
        print("🔧 Initializing COCO model...")
    
    coco_model = YOLO(config.COCO_MODEL_PATH)
    coco_model.to("cpu")
    
    if config.VERBOSE:
        print("✅ COCO model loaded")

def classify_vehicle(class_id: int) -> str:
    """Classify vehicle type"""
    if class_id in config.VEHICLES_4_WHEELS:
        return "to_check"
    
    if class_id in config.VEHICLES_2_WHEELS:
        return "authorized"
    
    return None

def detect_vehicles(frame: np.ndarray) -> list:
    """Detect vehicles in frame"""
    global coco_model
    
    results = coco_model(frame, verbose=False)[0]
    detections = []
    
    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = r
        class_id = int(class_id)
        
        if (score < config.DETECTION_CONFIDENCE or 
            class_id not in config.CLASSES_TO_DETECT):
            continue
        
        label = classify_vehicle(class_id)
        
        if label is None:
            continue
        
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        detections.append({
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            "score": score, "class_id": class_id, "label": label
        })
    
    return detections