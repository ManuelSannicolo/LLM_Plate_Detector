#import 
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from utils import get_car, read_plate, adjust_gamma
import config

#initialize tracker
tracker = Sort(
    max_age=config.TRACKER_MAX_AGE, 
    min_hits=config.TRACKER_MIN_HITS, 
    iou_threshold=config.TRACKER_IOU_THRESHOLD
)

#load models
coco_model = YOLO(config.COCO_MODEL_PATH)
plate_model = YOLO(config.PLATE_MODEL_PATH)

#video input
camera = cv2.VideoCapture(config.VIDEO_PATH)

#initialize dict
authorized_vehicles = {}
checked_vehicles = {}
plate_memory = {}
frame_count = 0

while True:
    ret, frame = camera.read()
    if not ret or frame is None:
        break
    
    frame_count += 1
    
    #detect vehicles
    results = coco_model(frame)[0]
    all_detections = []
    
    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = r
        class_id = int(class_id)
        
        if class_id not in config.CLASSES_TO_DETECT or score <= config.DETECTION_CONFIDENCE:
            continue
        
        label = None
        if class_id in config.VEHICLES_4_WHEELS:
            label = "to_check"
        elif class_id in config.VEHICLES_2_WHEELS:
            label = "authorized"
        elif class_id == 0:
            label = "pedestrian"
            
        all_detections.append({
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "score": score, "class_id": class_id,
            "label": label, "track_id": None
        })
    
    # Update tracker
    coordinates_for_tracker = [[d['x1'], d['y1'], d['x2'], d['y2'], d['score']] 
                                for d in all_detections]
    
    if len(coordinates_for_tracker) > 0:
        track_ids_vehicle = tracker.update(np.array(coordinates_for_tracker))
    else:
        track_ids_vehicle = []
    
    if len(track_ids_vehicle) != len(all_detections):
        continue
    
    for i in range(len(all_detections)):
        all_detections[i]['track_id'] = int(track_ids_vehicle[i][4])
    
    # Process vehicles
    for i, vehicle in enumerate(all_detections):
        track_id = vehicle['track_id']
        
        if track_id in checked_vehicles:
            all_detections[i]['label'] = checked_vehicles[track_id]
            continue
        
        if vehicle['label'] != "to_check":
            continue
        
        y1v, x1v = int(vehicle['y1']), int(vehicle['x1'])
        y2v, x2v = int(vehicle['y2']), int(vehicle['x2'])
        vehicle_cropped = frame[y1v:y2v, x1v:x2v]
        
        if vehicle_cropped.size == 0 or vehicle_cropped.shape[0] < 10:
            continue
        
        new_width = int((x2v-x1v) * 2)
        new_height = int((y2v-y1v) * 2)
        vehicle_cropped_resized = cv2.resize(
            vehicle_cropped, (new_width, new_height), 
            interpolation=cv2.INTER_CUBIC
        )
        
        license_plate_result = plate_model(vehicle_cropped_resized)[0]
        
        if len(license_plate_result.boxes) == 0:
            continue
        
        x1p, y1p, x2p, y2p, score, class_id = license_plate_result.boxes.data.tolist()[0]
        
        plate_cropped = vehicle_cropped[int(y1p/2):int(y2p/2), int(x1p/2):int(x2p/2)]
        
        if plate_cropped.size == 0 or plate_cropped.shape[0] < 10 or plate_cropped.shape[1] < 30:
            continue
        
        new_width = int((x2p-x1p) * 3)
        new_height = int((y2p-y1p) * 3)
        plate_cropped_resized = cv2.resize(
            plate_cropped, (new_width, new_height), 
            interpolation=cv2.INTER_CUBIC
        )
        
        plate_cropped_gray = cv2.cvtColor(plate_cropped_resized, cv2.COLOR_BGR2GRAY)
        plate_cropped_filtered = cv2.convertScaleAbs(
            plate_cropped_gray, alpha=1.5, beta=-2
        )
        
        plate_text, plate_score = read_plate(plate_cropped_filtered)
        
        if not plate_text:
            continue
        
        if plate_text in plate_memory:
            time_since = frame_count - plate_memory[plate_text]["last_seen_frame"]
            if time_since < config.MEMORY_FRAMES:
                status = plate_memory[plate_text]["status"]
                all_detections[i]['label'] = status
                plate_memory[plate_text]["last_seen_frame"] = frame_count
                continue
        
        # Use config authorized plates
        if plate_text in config.AUTHORIZED_PLATES:
            all_detections[i]['label'] = "authorized"
            checked_vehicles[track_id] = "authorized"
            plate_memory[plate_text] = {
                "status": "authorized", 
                "last_seen_frame": frame_count
            }
        else:
            all_detections[i]['label'] = "not authorized"
        
        with open(config.OUTPUT_CSV, "a") as f:
            f.write(f"{track_id},{plate_text},{plate_score}\n")

camera.release()
cv2.destroyAllWindows()
