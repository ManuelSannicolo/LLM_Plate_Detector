"""Vehicle processing utilities"""
import numpy as np
import server.config as config
from server.process.detection import extract_vehicle_crop, detect_plates_in_vehicle
from server.process.ocr_utils import find_best_plate_reading
from server.process.plate_utils import check_authorization, log_access_to_db, log_plate_result, log_to_csv

def process_vehicle_simple(vehicle_box: tuple, frame: np.ndarray,
                           track_id: int, frame_count: int) -> tuple:
    """Process single vehicle"""
    
    # Extract crop
    vehicle_crop = extract_vehicle_crop(vehicle_box, frame)
    
    if vehicle_crop.size == 0:
        return None, None, None, None
    
    if config.VERBOSE:
        print(f"\n{'='*60}")
        print(f"🚗 Processing Vehicle {track_id} | Frame {frame_count}")
        print(f"   Vehicle size: {vehicle_crop.shape[1]}x{vehicle_crop.shape[0]}")
    
    # Detect plates
    plates = detect_plates_in_vehicle(vehicle_crop)
    
    if not plates:
        if config.VERBOSE:
            print(f"   ✗ No plates detected")
        return None, None, None, None
    
    if config.VERBOSE:
        print(f"   ✓ {len(plates)} plates detected")
    
    # Find best reading
    best_result, best_confidence = find_best_plate_reading(plates, track_id, frame_count)
    
    if not best_result or best_confidence < config.OCR_MIN_CONFIDENCE:
        if config.VERBOSE:
            print(f"   ✗ No valid plate (confidence: {best_confidence:.2f})")
        return None, None, None, None
    
    # Check authorization
    status, plate_info = check_authorization(best_result)
    
    # Log
    log_plate_result(best_result, status, best_confidence, plate_info)
    log_to_csv(best_result, status, frame_count, best_confidence, track_id)
    log_access_to_db(best_result, status, frame_count, best_confidence, track_id)
    
    return best_result, best_confidence, plate_info, status

def process_detections(detections: list, frame: np.ndarray,
                       frame_count: int, checked_vehicles: dict):
    """Process all detections in frame"""
    
    for det in detections:
        if "track_id" not in det:
            continue
        
        track_id = det['track_id']
        
        # Use cached result
        if track_id in checked_vehicles:
            status, plate_text, plate_info = checked_vehicles[track_id]
            det['label'] = status
            det['plate_text'] = plate_text
            det['plate_info'] = plate_info
            continue
        
        # Only check 4-wheel vehicles
        if det['label'] != 'to_check':
            continue
        
        vehicle_box = (int(det['x1']), int(det['y1']),
                       int(det['x2']), int(det['y2']))
        
        # Process vehicle
        plate_text, score, plate_info, status = process_vehicle_simple(
            vehicle_box, frame, track_id, frame_count
        )
        
        # Update if valid
        if plate_text:
            det['label'] = status
            det['plate_text'] = plate_text
            det['plate_info'] = plate_info
            checked_vehicles[track_id] = (status, plate_text, plate_info)