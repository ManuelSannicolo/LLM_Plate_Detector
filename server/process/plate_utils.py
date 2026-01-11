"""Plate authorization and logging"""
import server.config as config
from server.control.context import get_context

def check_authorization(plate_text: str) -> tuple:
    """Check if plate is authorized"""
    db_manager = get_context("db_manager")
    
    if db_manager:
        try:
            is_authorized, plate_info = db_manager.is_plate_authorized(plate_text)
            
            if is_authorized:
                return "authorized", plate_info
            
            if plate_info and plate_info.get('status') == 'expired':
                return "expired", plate_info
            
            return "not_authorized", None
        
        except Exception as e:
            if config.VERBOSE:
                print(f"⚠️ Database error: {e}")
            
            if plate_text in config.ALL_AUTHORIZED_PLATES:
                return "authorized", {'plate_number': plate_text}
            
            return "not_authorized", None
    else:
        if plate_text in config.ALL_AUTHORIZED_PLATES:
            return "authorized", {'plate_number': plate_text}
        
        return "not_authorized", None

def log_access_to_db(plate_text: str, status: str, frame_number: int,
                     confidence: float, track_id: int):
    """Log access to database"""
    db_manager = get_context("db_manager")
    
    if db_manager:
        try:
            db_manager.log_access(
                plate_number=plate_text,
                frame_number=frame_number,
                confidence=confidence,
                status=status,
                track_id=track_id
            )
        except Exception as e:
            print(f"❌ Error logging to DB: {e}")

def log_to_csv(plate_text: str, status: str, frame_number: int,
               confidence: float, track_id: int):
    """Log to CSV file"""
    with open(config.OUTPUT_CSV, 'a') as f:
        f.write(f"{plate_text},{status},{frame_number},{confidence},{track_id}\n")

def log_plate_result(plate_text: str, status: str, confidence: float, plate_info: dict):
    """Print plate result to console"""
    if not config.VERBOSE:
        return
    
    print(f"\n   📋 PLATE: {plate_text}")
    print(f"   🎯 Confidence: {confidence:.2f}")
    
    if status == "authorized":
        print(f"   ✅ AUTHORIZED")
        if plate_info:
            print(f"   Owner: {plate_info.get('first_name')} {plate_info.get('last_name')}")
    elif status == "expired":
        print(f"   ⚠️ EXPIRED")
    else:
        print(f"   ❌ NOT AUTHORIZED")