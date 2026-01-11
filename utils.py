import string
import easyocr
import cv2
import numpy as np

# Initialize OCR readers
easyocr_reader = easyocr.Reader(['en'], gpu=False)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Character correction dictionaries
similar_char_to_int = {
    'O': '0', 'I': '1', 'J': '3', 
    'A': '4', 'G': '6', 'S': '5',
    'Z': '2', 'B': '8', 'Q': '0'
}

similar_int_to_char = {
    '0': 'O', '1': 'I', '3': 'J', 
    '4': 'A', '6': 'G', '5': 'S',
    '2': 'Z', '8': 'B'
}

def get_car(plate_coordinates, vehicle_ids):
    """Find vehicle that contains the plate"""
    x1, y1, x2, y2 = plate_coordinates
    
    for vehicle in vehicle_ids:
        xcar1, ycar1, xcar2, ycar2, vehicle_id = vehicle
        
        if x1 > xcar1 and x2 < xcar2 and y1 > ycar1 and y2 < ycar2:
            return vehicle
    
    return -1, -1, -1, -1, -1

def read_plate(plate_image):
    """Read plate using multiple OCR methods"""
    results = []
    
    # Method 1: EasyOCR
    text1, score1 = read_plate_easyocr(plate_image)
    if text1:
        results.append((text1, score1, "easyocr"))
    
    # Method 2: Tesseract (fallback)
    if TESSERACT_AVAILABLE:
        text2, score2 = read_plate_tesseract(plate_image)
        if text2:
            results.append((text2, score2, "tesseract"))
    
    if not results:
        return None, 0.0
    
    # Select best result
    best = max(results, key=lambda x: x[1])
    return best[0], best[1]

def read_plate_easyocr(plate_image):
    """Read plate with EasyOCR"""
    results = easyocr_reader.readtext(plate_image)
    
    for result in results:
        bounding_box, plate_text, plate_score = result
        plate_text = plate_text.upper().replace(" ", "")
        
        if len(plate_text) >= 6:
            if plate_format_check(plate_text):
            return improve_plate_text(plate_text), plate_score
        return improve_plate_text(plate_text), plate_score * 0.5  # Lower confidence if invalid format
    
    return None, 0.0

def read_plate_tesseract(plate_image):
    """Read plate with Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        return None, 0.0
    
    try:
        # Convert to grayscale if needed
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        
        # Threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Config for plates
        config = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        text = pytesseract.image_to_string(thresh, config=config)
        text = text.upper().replace(" ", "").replace("\n", "")
        
        if len(text) >= 6:
            return improve_plate_text(text), 0.8
        
        return None, 0.0
    except Exception as e:
        return None, 0.0

def plate_format_check(plate_text):
    """Validate Italian plate format AA000AA"""
    if len(plate_text) != 7:
        return False
    
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    if plate_text[0] not in string.ascii_uppercase and plate_text[0] not in similar_int_to_char.keys():
        return False
    if plate_text[1] not in string.ascii_uppercase and plate_text[1] not in similar_int_to_char.keys():
        return False
    
    for i in [2, 3, 4]:
        if plate_text[i] not in digits and plate_text[i] not in similar_char_to_int.keys():
            return False
    
    if plate_text[5] not in string.ascii_uppercase and plate_text[5] not in similar_int_to_char.keys():
        return False
    if plate_text[6] not in string.ascii_uppercase and plate_text[6] not in similar_int_to_char.keys():
        return False
    
    return True

def improve_plate_text(plate_text):
    """Correct OCR mistakes based on character position"""
    if len(plate_text) < 7:
        return plate_text
    
    # Truncate if too long
    if len(plate_text) > 7:
        plate_text = plate_text[:7]
    
    improved_text = ""
    
    for i, char in enumerate(plate_text):
        if i in [0, 1, 5, 6]:  # Letters
            if char in similar_int_to_char.keys():
                improved_text += similar_int_to_char[char]
            else:
                improved_text += char
        else:  # Digits
            if char in similar_char_to_int.keys():
                improved_text += similar_char_to_int[char]
            else:
                improved_text += char
    
    return improved_text

def adjust_gamma(image, gamma=1.5):
    """Adjust image gamma"""
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)
