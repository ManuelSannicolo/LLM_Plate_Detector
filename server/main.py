"""Main server processing"""
from ultralytics import YOLO
import cv2
from sort.sort import Sort
import time
import threading

try:
    from fast_plate_ocr import LicensePlateRecognizer
except ImportError:
    LicensePlateRecognizer = None

import server.config as config
from server.control.context import set_context, get_context
from server.process.vehicle_utils import process_detections
from server.process.detection import update_tracking
from server.database import DatabaseManager
from server.control.frame_queue import frame_queue

# Global
recognizer = None
db_manager = None
stop_threads = threading.Event()

def initialize_ocr():
    """Initialize OCR"""
    global recognizer
    
    if config.VERBOSE:
        print("🔧 Initializing OCR...")
    
    try:
        import pytesseract
        config.TESSERACT_AVAILABLE = True
        if config.VERBOSE:
            print("✅ Tesseract available")
    except ImportError:
        config.TESSERACT_AVAILABLE = False
        if config.VERBOSE:
            print("❌ Tesseract not available")
    
    try:
        if LicensePlateRecognizer:
            recognizer = LicensePlateRecognizer("cct-xs-v1-global-model")
            config.FAST_OCR_AVAILABLE = True
            if config.VERBOSE:
                print("✅ Fast Plate OCR available")
            set_context("recognizer", recognizer)
    except Exception as e:
        config.FAST_OCR_AVAILABLE = False
        if config.VERBOSE:
            print(f"❌ Fast Plate OCR error: {e}")

def initialize_database():
    """Initialize database"""
    global db_manager
    
    try:
        db_manager = DatabaseManager(config.DATABASE_PATH)
        if config.VERBOSE:
            print("✅ DatabaseManager initialized")
        
        set_context("db_manager", db_manager)
    
    except Exception as e:
        print(f"❌ DatabaseManager init error: {e}")

def load_models():
    """Load YOLO models"""
    if config.VERBOSE:
        print("   Loading YOLO models...")
    
    coco_model = YOLO(config.COCO_MODEL_PATH)
    coco_model.to(config.DEVICE)
    
    plate_model = YOLO(config.PLATE_MODEL_PATH)
    plate_model.to(config.DEVICE)
    
    set_context("coco_model", coco_model)
    set_context("plate_model", plate_model)

def initialize_tracker():
    """Initialize SORT tracker"""
    if config.VERBOSE:
        print("   Initializing SORT tracker...")
    
    tracker = Sort(
        max_age=config.TRACKER_MAX_AGE,
        min_hits=config.TRACKER_MIN_HITS,
        iou_threshold=config.TRACKER_IOU_THRESHOLD
    )
    
    set_context("tracker", tracker)

def processing_thread():
    """Main processing thread"""
    if config.VERBOSE:
        print("🚀 Initializing system...")
        print(f"   Device: {config.DEVICE}")
        print(f"   Frame source: {config.FRAME_SOURCE}")
    
    load_models()
    initialize_tracker()
    
    # State
    checked_vehicles = {}
    frame_count = 0
    
    if config.VERBOSE:
        print("\n🎬 Starting processing...\n")
    
    start_time = time.time()
    
    try:
        while not stop_threads.is_set():
            # Get frame from queue
            if frame_queue.empty():
                time.sleep(0.1)
                if config.VERBOSE and frame_count == 0:
                    print("⏳ Waiting for frames...")
                continue
            
            data = frame_queue.get()
            frame = data[0]
            metadata = data[1]
            
            if frame is None:
                if config.VERBOSE:
                    print("⚠️ Invalid frame")
                continue
            
            frame_count += 1
            
            if config.VERBOSE and frame_count % 100 == 0:
                elapsed = time.time() - start_time
                print(f"📊 Frame {frame_count} | FPS: {frame_count/elapsed:.1f}")
            
            # Get detections from metadata
            detections = metadata.get("detections", [])
            
            # Update tracking
            detections = update_tracking(detections)
            
            # Process detections
            process_detections(detections, frame, frame_count, checked_vehicles)
    
    except KeyboardInterrupt:
        if config.VERBOSE:
            print("\n⚠️ User interrupt")
    
    finally:
        stop_threads.set()
        if config.VERBOSE:
            elapsed = time.time() - start_time
            print(f"\n✅ COMPLETED!")
            print(f"Time: {elapsed:.1f}s | FPS: {frame_count/elapsed:.1f}")
            print(f"Vehicles checked: {len(checked_vehicles)}")

if __name__ == "__main__":
    initialize_ocr()
    initialize_database()
    
    thread = threading.Thread(target=processing_thread)
    thread.start()
    
    try:
        thread.join()
    except KeyboardInterrupt:
        stop_threads.set()
        thread.join(timeout=2)