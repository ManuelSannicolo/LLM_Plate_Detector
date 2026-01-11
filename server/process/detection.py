"""Detection and tracking module"""
from ultralytics import YOLO
from sort.sort import Sort
import numpy as np
import server.config as config
from server.control.context import get_context

def update_tracking(detections: list) -> list:
    """Update SORT tracker with detections"""
    tracker = get_context("tracker")
    if not detections:
        return detections
    
    coords = [[float(d['x1']), float(d['y1']), float(d['x2']), 
               float(d['y2']), float(d['score'])] for d in detections]
    
    track_ids = tracker.update(np.array(coords))
    
    if len(track_ids) == len(detections):
        for i, det in enumerate(detections):
            det['track_id'] = int(track_ids[i][4])
    
    return detections

def detect_plates_in_vehicle(vehicle_crop: np.ndarray) -> list:
    """Detect plates in vehicle crop"""
    plate_model = get_context("plate_model")
    
    results = plate_model(vehicle_crop, conf=config.PLATE_DETECTION_CONFIDENCE, verbose=False)[0]
    
    plates = []
    
    for box in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Validate dimensions
        width = x2 - x1
        height = y2 - y1
        
        if width < 30 or height < 10:
            continue
        
        aspect_ratio = width / float(height)
        if aspect_ratio < 1.5 or aspect_ratio > 7.0:
            continue
        
        plate_crop = vehicle_crop[y1:y2, x1:x2]
        
        if plate_crop.size > 0:
            plates.append({
                'image': plate_crop,
                'coords': (x1, y1, x2, y2),
                'score': score
            })
    
    return plates

def extract_vehicle_crop(vehicle_box: tuple, frame: np.ndarray) -> np.ndarray:
    """Extract vehicle crop with margin"""
    x1, y1, x2, y2 = vehicle_box
    
    margin = config.VEHICLE_CROP_MARGIN
    
    x1_crop = max(0, x1 - margin)
    y1_crop = max(0, y1 - margin)
    x2_crop = min(frame.shape[1], x2 + margin)
    y2_crop = min(frame.shape[0], y2 + margin)
    
    return frame[y1_crop:y2_crop, x1_crop:x2_crop]