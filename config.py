"""
Configuration file for plate detection system
"""
import os

# Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(APP_DIR, "models")

# Models
COCO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n.pt")
PLATE_MODEL_PATH = os.path.join(MODELS_DIR, "best.pt")

# Video source
VIDEO_PATH = "video3.mp4"
USE_WEBCAM = False

# Detection parameters
DETECTION_CONFIDENCE = 0.2
PLATE_DETECTION_CONFIDENCE = 0.2

# COCO classes to detect
CLASSES_TO_DETECT = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck
VEHICLES_4_WHEELS = [2, 5, 7]  # car, bus, truck
VEHICLES_2_WHEELS = [1, 3]  # bicycle, motorcycle

# Tracker parameters (SORT)
TRACKER_MAX_AGE = 30
TRACKER_MIN_HITS = 3
TRACKER_IOU_THRESHOLD = 0.3

# Memory
MEMORY_FRAMES = 300  # ~10 seconds at 30fps

# Output
OUTPUT_CSV = "detected_plates.csv"

# Authorized plates (temporary, will move to database)
AUTHORIZED_PLATES = ["NA13NRU", "GX150GJ"]

# Verbose
VERBOSE = True
