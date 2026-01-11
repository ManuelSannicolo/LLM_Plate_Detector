#import 
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort
from utils import get_car, read_plate, adjust_gamma

#initialize tracker --> vehicle tracker
tracker = Sort(max_age=30, min_hits=3, iou_threshold=0.3)

#load models
coco_model = YOLO("./models/yolov8n.pt")
plate_model = YOLO("./models/best.pt")

#video input
camera = cv2.VideoCapture("video3.mp4")

#define COCO classes to detect
to_detect = [0,1,2,3,5,7]
vehicle_to_check = [2,5,7]

#initialize dict to store vehicle tracking
authorized_vehicles = {}
checked_vehicles = {}  # {track_id: status}
plate_memory = {}  # {plate_text: {"status": str, "last_seen_frame": int}}
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
        
        if class_id not in to_detect or score <= 0.2:
            continue
        
        label = None
        if class_id in vehicle_to_check:
            label = "to_check"
        elif class_id in [1,3]:
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
    
    # Assign track_id
    for i in range(len(all_detections)):
        all_detections[i]['track_id'] = int(track_ids_vehicle[i][4])
    
    # Process vehicles
    for i, vehicle in enumerate(all_detections):
        track_id = vehicle['track_id']
        
        # Use cached result if already checked
        if track_id in checked_vehicles:
            all_detections[i]['label'] = checked_vehicles[track_id]
            continue
        
        if vehicle['label'] != "to_check":
            continue
        
        # Crop vehicle
        y1v, x1v = int(vehicle['y1']), int(vehicle['x1'])
        y2v, x2v = int(vehicle['y2']), int(vehicle['x2'])
        vehicle_cropped = frame[y1v:y2v, x1v:x2v]
        
        if vehicle_cropped.size == 0 or vehicle_cropped.shape[0] < 10:
            continue
        
        # Resize for better detection
        new_width = int((x2v-x1v) * 2)
        new_height = int((y2v-y1v) * 2)
        vehicle_cropped_resized = cv2.resize(
            vehicle_cropped, (new_width, new_height), 
            interpolation=cv2.INTER_CUBIC
        )
        
        # Detect license plate
        license_plate_result = plate_model(vehicle_cropped_resized)[0]
        
        if len(license_plate_result.boxes) == 0:
            continue
        
        x1p, y1p, x2p, y2p, score, class_id = license_plate_result.boxes.data.tolist()[0]
        
        # Crop plate
        plate_cropped = vehicle_cropped[int(y1p/2):int(y2p/2), int(x1p/2):int(x2p/2)]
        
        if plate_cropped.size == 0 or plate_cropped.shape[0] < 10 or plate_cropped.shape[1] < 30:
            continue
        
        new_width = int((x2p-x1p) * 3)
        new_height = int((y2p-y1p) * 3)
        plate_cropped_resized = cv2.resize(
            plate_cropped, (new_width, new_height), 
            interpolation=cv2.INTER_CUBIC
        )
        
        # Preprocess
        plate_cropped_gray = cv2.cvtColor(plate_cropped_resized, cv2.COLOR_BGR2GRAY)
        plate_cropped_filtered = cv2.convertScaleAbs(
            plate_cropped_gray, alpha=1.5, beta=-2
        )
        
        # Read plate
        plate_text, plate_score = read_plate(plate_cropped_filtered)
        
        if not plate_text:
            continue
        
        # Check memory
        if plate_text in plate_memory:
            time_since = frame_count - plate_memory[plate_text]["last_seen_frame"]
            if time_since < 300:
                status = plate_memory[plate_text]["status"]
                all_detections[i]['label'] = status
                plate_memory[plate_text]["last_seen_frame"] = frame_count
                continue
        
        # Check authorization (hardcoded for now)
        if plate_text in ["NA13NRU", "GX150GJ"]:
            all_detections[i]['label'] = "authorized"
            checked_vehicles[track_id] = "authorized"
            plate_memory[plate_text] = {
                "status": "authorized", 
                "last_seen_frame": frame_count
            }
        else:
            all_detections[i]['label'] = "not authorized"
        
        # Save to CSV
        with open("detected_plates.csv", "a") as f:
            f.write(f"{track_id},{plate_text},{plate_score}\n")

camera.release()
cv2.destroyAllWindows()
