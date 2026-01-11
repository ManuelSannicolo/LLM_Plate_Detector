"""OCR utilities for plate reading"""
import cv2
import numpy as np
import server.config as config

# Character correction
INT_POS_CORRECTION = {
    'O': '0', 'Q': '0', 'I': '1', 'Z': '2', 
    'S': '5', 'B': '8'
}

CHAR_POS_CORRECTION = {
    '0': 'D', '1': 'L', '2': 'Z', '5': 'S', 
    '8': 'B', 'O': 'D', 'Q': 'D'
}

def preprocess_plate(plate_img: np.ndarray) -> np.ndarray:
    """Preprocess plate image"""
    if len(plate_img.shape) == 3:
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = plate_img.copy()
    
    # Resize
    h, w = gray.shape
    target_height = 120
    if h < target_height:
        scale = target_height / h
        resized = cv2.resize(gray, (int(w * scale), target_height), 
                             interpolation=cv2.INTER_CUBIC)
    else:
        resized = gray
    
    # Enhance
    brightness = np.mean(resized)
    if brightness < 100:
        resized = cv2.equalizeHist(resized)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(resized, None, h=10)
    
    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

def clean_ocr_text(text: str) -> str:
    """Clean OCR output"""
    import re
    text_clean = text.upper().replace(" ", "")
    text_clean = re.sub(r'[^A-Z0-9]', '', text_clean)
    return text_clean

def improve_plate_text(text: str) -> str:
    """Correct OCR errors based on position"""
    if len(text) < 7:
        return None
    
    if len(text) > 7:
        text = text[:7]
    
    result = ""
    
    for i, char in enumerate(text):
        if i in [0, 1, 5, 6]:  # Letters
            if char in CHAR_POS_CORRECTION:
                result += CHAR_POS_CORRECTION[char]
            else:
                result += char
        else:  # Digits
            if char in INT_POS_CORRECTION:
                result += INT_POS_CORRECTION[char]
            else:
                result += char
    
    return result

def process_plate_ocr(plate_img: np.ndarray, track_id: int, 
                      frame_count: int, plate_index: int) -> tuple:
    """Process plate with OCR"""
    # Preprocess
    preprocessed = preprocess_plate(plate_img)
    
    # OCR (placeholder - will implement multi-method later)
    # For now return dummy
    return "AB123CD", 0.85, "dummy"

def find_best_plate_reading(plates: list, track_id: int, 
                            frame_count: int) -> tuple:
    """Find best plate reading from multiple detections"""
    best_result = None
    best_confidence = 0.0
    
    for i, plate_data in enumerate(plates):
        plate_img = plate_data['image']
        detection_score = plate_data['score']
        
        plate_text, ocr_conf, method = process_plate_ocr(
            plate_img, track_id, frame_count, i
        )
        
        if not plate_text:
            continue
        
        if ocr_conf > best_confidence:
            best_result = plate_text
            best_confidence = ocr_conf
    
    return best_result, best_confidence