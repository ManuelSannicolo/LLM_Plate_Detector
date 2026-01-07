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
        license_plate_result = plate_model(vehicle_cropped_resized)[0]
        
        if len(license_plate_result.boxes) == 0:
            print("nessuna targa trovata")
            continue
        
        #data of the license plate detected
        x1p, y1p, x2p, y2p, score, class_id = license_plate_result.boxes.data.tolist()[0]
        
        #convert the coordinates of the license plate to the original frame
        #the cropped frame does not modify the proportions of the veichle
        #therefore we can just add the coordinated of the vehicle to the coordinates of the plate
        x1_abs = x1v + int(x1p)
        y1_abs = y1v + int(y1p)
        x2_abs = x1v + int(x2p)
        y2_abs = y1v + int(y2p)
        
        
        
        #assign the plate to the vehicle
        xcar1, ycar1, xcar2, ycar2, vehicle_id = get_car ((x1_abs, y1_abs, x2_abs, y2_abs), track_ids_vehicle)
        
        #if no vehicle found with the corrisponding license plate continue
        if vehicle_id == -1:
            continue
        
        #crop the license plate from the vehicle image
        plate_cropped = vehicle_cropped[int(y1p/2):int(y2p/2), int(x1p/2):int(x2p/2)]
        
        if plate_cropped.size == 0 or plate_cropped.shape[0] < 2 or plate_cropped.shape[1] < 2:
            print("plate too small to process")
            continue
        
        new_width = int((x2p-x1p) * 3)
        new_height = int((y2p-y1p) * 3)
        plate_cropped_resized = cv2.resize(plate_cropped, (new_width,new_height), interpolation=cv2.INTER_CUBIC)
        
        
        # cv2.imshow("Plate", plate_cropped)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        #preprocess the plate for better OCR results
        #convert to grayscale
        plate_cropped_gray = cv2.cvtColor(plate_cropped_resized, cv2.COLOR_BGR2GRAY)
        #increase contrast and brightness
        plate_croppef_filtered = cv2.convertScaleAbs(plate_cropped_gray, alpha=1.5, beta=-2)
        # _, thresh = cv2.threshold(plate_cropped_gray, 150, 255, cv2.THRESH_BINARY)

        
        
        #read the plate
        plate_text, plate_score = read_plate(plate_croppef_filtered)
        print ("\n"*10, plate_text)
        
        
        if plate_text == None or plate_text == "":
            print("problemaaaaa")
            continue

        print(plate_text)
        
        
        #assign the license plate to the vehicle
        
        if plate_text in plate_memory:
            time_since_last_seen = frame_count - plate_memory[plate_text]["last_seen_frame"]
            if time_since_last_seen < 300:  # Visto negli ultimi 10 secondi
                # Usa lo status salvato in memoria
                status = plate_memory[plate_text]["status"]
                all_detections[i]['label'] = status
                plate_memory[plate_text]["last_seen_frame"] = frame_count  # Aggiorna ultimo frame visto
                print(f"→ Targa {plate_text} già vista recentemente: {status}")
                continue

        
        #check if the vehicle is authorized
                
        if plate_text =="NA13NRU" or plate_text == "GX150GJ":
            all_detections[i]['label'] = "authorized"
            checked_vehicles[track_id] = "authorized"
            authorized_vehicles[track_id] = plate_text
            plate_memory[plate_text] = {"status": "authorized", "last_seen_frame": frame_count}


        else:
            all_detections[i]['label'] = "not authorized"
            
            
            
            
        
        #add in csv
        #with vehicle_id, plate_text, plate_score
        with open("detected_plates.csv", "a") as f:
            f.write(f"{track_id},{plate_text},{plate_score}\n")
            
            
        
        
    # new_frame = draw_boxes(frame, all_detections)
    # valid = show_frame(new_frame)
    # if not valid:
    #     break        
        
      
        
        
camera.release()
cv2.destroyAllWindows()