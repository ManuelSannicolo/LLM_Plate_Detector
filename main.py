#import 
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import Sort


#initialize tracker --> vehicle tracker
tracker = Sort(max_age=30, min_hits=3, iou_threshold=0.3)
#load models
coco_model = YOLO("./models/yolov8n.pt")
plate_model = YOLO("./models/best.pt")


# testo_targa = read_plate("targa.png")
# print(testo_targa)

#video input
camera = cv2.VideoCapture("video3.mp4") #main camera


#define COCO classes to detect
to_detect = [0,1,2,3,5,7] #person, bicycle, car, motorcycle, bus, truck
vehicle_to_check = [2,5,7] #car, bus, truck


#initialize dict to store authorized plates
authorized_vehicles = {}  # {track_id: plate_text}
checked_vehicles = {}  # {track_id: status} --> "authorized" or "not authorized"
plate_memory = {}  # {plate_text: {"status": "authorized/not authorized", "last_seen_frame": int}}
frame_count = 0 



while True:
    #valid = True if the frame is captured correctly
    ret, frame = camera.read()
    if not ret or frame is None:
        break
    
    frame_count += 1  
    
    #detect vehicles
    results = coco_model(frame)[0]
    #array to store the image data (x,y) of the vehicles detected
    all_detections = []
    for r in results.boxes.data.tolist():
        #composition of r: x1, y1, x2, y2, score, class_id
        x1, y1, x2, y2, score, class_id = r
        
        class_id = int(class_id)
        
        
        #check if the object detected is in the classes to detect and if the score is > 0.5
        if class_id not in to_detect or score <= 0.3:
            continue
        
        print(f"Detected class id: {class_id} with score: {score}")
        
        
        label = None


        if class_id in vehicle_to_check:
            label = "to_check"
        #check if the object detected is bycicle or a motorcycle --> authorized
        elif class_id in [1,3]:
            label = "authorized"
        #check if the object detected is a person --> not need to be authorized, just tracked
        elif class_id == 0:
            label = "pedestrian"
            
        all_detections.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "score": score, "class_id": class_id, "label": label, "track_id": None})
    
    
    #convert all_detections to the format required by the tracker
    #x1, y1, x2, y2, score
    coordinates_for_tracker = [[d['x1'], d['y1'], d['x2'], d['y2'], d['score']] for d in all_detections]

    #id to assign to the vehicle (unique)
    if len(coordinates_for_tracker) > 0:
        track_ids_vehicle = tracker.update(np.array(coordinates_for_tracker))
    else:
        track_ids_vehicle = []
    
    
    
    if len(track_ids_vehicle) != len(all_detections):
        print("Mismatch between tracker outputs and detections")
        continue
    
    #assign track_id to all_detections
    for i in range (len(all_detections)):
        all_detections[i]['track_id'] = int(track_ids_vehicle[i][4])
        
    
    
    
    
    #cropping vehicles images
    #use enumerate to have the index of the vehicle
    for i, vehicle in enumerate(all_detections):
        
        track_id = vehicle['track_id']
        

        #check if the vehicle has already been checked 
        if track_id in checked_vehicles and checked_vehicles[track_id] == "authorized":
            all_detections[i]['label'] = checked_vehicles[track_id]
            continue

        
        #check if the object detected is a vehicle to check
        if vehicle['label'] != "to_check":
            continue
        
        
        
        #crop the vehicle from the frame
        y1v, x1v, y2v, x2v = int(vehicle['y1']), int(vehicle['x1']), int(vehicle['y2']), int(vehicle['x2'])
        vehicle_cropped = frame[y1v:y2v, x1v:x2v]
        
        if vehicle_cropped.size == 0 or vehicle_cropped.shape[0] < 10 or vehicle_cropped.shape[1] <10:
            print("vehicle too small to process")
            continue
        
        new_width = int((x2v-x1v) * 2)
        new_height = int((y2v-y1v) * 2)

        vehicle_cropped_resized = cv2.resize(vehicle_cropped, (new_width,new_height), interpolation=cv2.INTER_CUBIC)
        
        

       
        #detect license plate
        
        
        
        
camera.release()
cv2.destroyAllWindows()