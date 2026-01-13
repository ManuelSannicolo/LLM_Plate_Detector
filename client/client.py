"""Client - sends frames to server via HTTP"""
import cv2
import requests
import time
import json
from detection import initialize_coco_model, detect_vehicles
import config

SERVER_URL = "http://localhost:5000/api/upload"

headers = {
    "camera-id": "camera_client01",
    "API-Key": "g9f3e1d7c4b84eab9f5c1d2e3a4b57kd"
}

def send_single_frame(frame_path):
    """Send single frame from file"""
    frame = cv2.imread(frame_path)
    if frame is None:
        if config.VERBOSE:
            print(f"❌ Cannot read {frame_path}")
        return False
    
    detections = detect_vehicles(frame) or []
    if not detections or len(detections) == 0:
        if config.VERBOSE:
            print("   No vehicles detected")
        return True
    
    _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    files = {"image": ("frame.jpg", jpg.tobytes(), "image/jpeg")}
    data = {"metadata": json.dumps({"detections": detections})}
    
    try:
        response = requests.post(
            SERVER_URL, files=files, data=data,
            timeout=0.1, headers=headers
        )
        
        if response.ok:
            if config.VERBOSE:
                print(f"✅ Frame sent: {response.json()}")
            return True
        else:
            if config.VERBOSE:
                print(f"❌ Server error: {response.status_code} - {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        if config.VERBOSE:
            print(f"❌ Request error: {e}")
        return False

def send_video_stream(source=0, fps=10):
    """Send frames from webcam/video"""
    try:
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            if config.VERBOSE:
                print(f"❌ Cannot open video source: {source}")
            return
        
        print(f"📹 Streaming from: {source if isinstance(source, str) else 'Webcam'}")
        print(f"   Target FPS: {fps}")
        print("   Press 'q' to exit\n")
        
        frame_delay = 1.0 / fps
        frame_count = 0
        success_count = 0
        
        while True:
            start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                if config.VERBOSE:
                    print("⚠️ End of stream")
                break
            
            detections = detect_vehicles(frame) or []
            if not detections or len(detections) == 0:
                if config.VERBOSE:
                    print("   No vehicles in frame")
                continue
            
            _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            files = {"image": ("frame.jpg", jpg.tobytes(), "image/jpeg")}
            data = {"metadata": json.dumps({"detections": detections})}
            
            try:
                response = requests.post(
                    SERVER_URL, files=files, data=data,
                    timeout=0.3, headers=headers
                )
                
                if response.ok:
                    success_count += 1
                    status = "✅"
                    if config.VERBOSE:
                        print("✅ Frame sent")
                else:
                    status = f"❌ {response.status_code}"
                    if config.VERBOSE:
                        print(f"❌ Server error: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                status = f"❌ {type(e).__name__}"
            
            frame_count += 1
            
            if config.VERBOSE and frame_count % 30 == 0:
                print(f"Frames: {frame_count} | Success: {success_count}/{frame_count} | Status: {status}")
            
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
        
        cap.release()
        cv2.destroyAllWindows()
        
        if config.VERBOSE:
            print(f"\n📊 Summary:")
            print(f"   Total frames: {frame_count}")
            print(f"   Sent successfully: {success_count}")
            print(f"   Success rate: {(success_count/frame_count*100):.1f}%")
    
    except KeyboardInterrupt:
        if config.VERBOSE:
            print("\n⚠️ Keyboard interrupt")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    initialize_coco_model()
    
    # Test with single frame
    send_single_frame("test_frame.jpg")
    
    # Or stream video
    # send_video_stream("video3.mp4", fps=30)