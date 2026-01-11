"""Client - sends frames to server"""
import cv2
import requests
import time
import json
from detection import initialize_coco_model, detect_vehicles
import config

SERVER_URL = "http://localhost:5000/api/upload"

#headers with authentication
headers = {
    "camera-id": "camera_client01",
    "API-Key": "g9f3e1d7c4b84eab9f5c1d2e3a4b57kd"
}

def send_single_frame(frame_path):
    """Send single frame to server"""
    frame = cv2.imread(frame_path)
    if frame is None:
        print(f"❌ Cannot read {frame_path}")
        return False
    
    detections = detect_vehicles(frame) or []
    
    if not detections:
        if config.VERBOSE:
            print("   No vehicles detected")
        return True
    
    #encode and send
    _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    files = {"image": ("frame.jpg", jpg.tobytes(), "image/jpeg")}
    data = {"metadata": json.dumps({"detections": detections})}
    
    try:
        response = requests.post(
            SERVER_URL, files=files, data=data,
            timeout=0.3, headers=headers
        )
        
        if response.ok:
            if config.VERBOSE:
                print(f"✅ Frame sent: {response.json()}")
            return True
        else:
            if config.VERBOSE:
                print(f"❌ Server error: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        if config.VERBOSE:
            print(f"❌ Request error: {e}")
        return False

if __name__ == "__main__":
    initialize_coco_model()
    send_single_frame("test_frame.jpg")