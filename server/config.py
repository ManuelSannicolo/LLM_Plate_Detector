"""
Configuration file for plate detection system
"""
import os

# -------------------------
#paths
# -------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(APP_DIR, "models")
DATA_DIR = os.path.join(APP_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "plates.db")

# -------------------------
#models
# -------------------------
COCO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n.pt")
PLATE_MODEL_PATH = os.path.join(MODELS_DIR, "best.pt")

# -------------------------
#video source
# -------------------------
VIDEO_PATH = "video3.mp4"
USE_WEBCAM = False

# -------------------------
#detection parameters
# -------------------------
DETECTION_CONFIDENCE = 0.2
PLATE_DETECTION_CONFIDENCE = 0.2
OCR_MIN_CONFIDENCE = 0.75

#COCO classes to detect
CLASSES_TO_DETECT = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck
VEHICLES_4_WHEELS = [2, 5, 7]  # car, bus, truck
VEHICLES_2_WHEELS = [1, 3]      # bicycle, motorcycle

# -------------------------
#tracker parameters (SORT)
# -------------------------
TRACKER_MAX_AGE = 30
TRACKER_MIN_HITS = 3
TRACKER_IOU_THRESHOLD = 0.3

# -------------------------
#memory
# -------------------------
MEMORY_FRAMES = 300  # ~10 seconds at 30fps

# -------------------------
#CSV output
# -------------------------
OUTPUT_CSV = os.path.join(DATA_DIR, "detected_plates.csv")

# -------------------------
#authorized plates
# -------------------------
ALL_AUTHORIZED_PLATES = []

def load_authorized_plates():
    """Load plates from database"""
    try:
        from server.database import DatabaseManager
        
        if not os.path.exists(DATABASE_PATH):
            return []
        
        db = DatabaseManager(DATABASE_PATH)
        plates = db.get_all_valid_plates()
        db.close()
        
        return plates
    except Exception as e:
        print(f"⚠️ Warning: Could not load authorized plates: {e}")
        return []

ALL_AUTHORIZED_PLATES = load_authorized_plates()

# -------------------------
#vehicle processing
# -------------------------
VEHICLE_CROP_MARGIN = 10

# -------------------------
#verbose
# -------------------------
VERBOSE = True

#camera authentication
AUTHORIZED_CAMERAS = {
    "camera_client01": "g9f3e1d7c4b84eab9f5c1d2e3a4b57kd"
}

REQUIRE_CAMERA_AUTH = True