"""Client configuration"""
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "yolo")

#detection parameters
DETECTION_CONFIDENCE = 0.2
CLASSES_TO_DETECT = [0, 1, 2, 3, 5, 7]
VEHICLES_4_WHEELS = [2, 5, 7]
VEHICLES_2_WHEELS = [1, 3]

#model path
COCO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n.pt")

#verbose
VERBOSE = True
