import string
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

# Dictionaries for character correction
similar_char_to_int = {
    'O': '0', 'I': '1', 'J': '3', 
    'A': '4', 'G': '6', 'S': '5',
    'Z': '2', 'B': '8'
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
    """Read plate text using EasyOCR"""
    results = reader.readtext(plate_image)
    
    for result in results:
        bounding_box, plate_text, plate_score = result
        
        plate_text = plate_text.upper().replace(" ", "")
        
        if plate_format_check(plate_text):
            return improve_plate_text(plate_text), plate_score
        
        return improve_plate_text(plate_text), plate_score
    
    return None, 0.0

def plate_format_check(plate_text):
    """Validate Italian plate format AA000AA"""
    if len(plate_text) != 7:
        return False
    
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    # First two: letters
    if plate_text[0] not in string.ascii_uppercase and plate_text[0] not in similar_int_to_char.keys():
        return False
    if plate_text[1] not in string.ascii_uppercase and plate_text[1] not in similar_int_to_char.keys():
        return False
    
    # Middle three: digits
    for i in [2, 3, 4]:
        if plate_text[i] not in digits and plate_text[i] not in similar_char_to_int.keys():
            return False
    
    # Last two: letters
    if plate_text[5] not in string.ascii_uppercase and plate_text[5] not in similar_int_to_char.keys():
        return False
    if plate_text[6] not in string.ascii_uppercase and plate_text[6] not in similar_int_to_char.keys():
        return False
    
    return True

def improve_plate_text(plate_text):
    """Correct common OCR mistakes based on position"""
    improved_text = ""
    
    for i, char in enumerate(plate_text):
        # Positions 0,1,5,6: should be letters
        if i in [0, 1, 5, 6]:
            if char in similar_int_to_char.keys():
                improved_text += similar_int_to_char[char]
            else:
                improved_text += char
        # Positions 2,3,4: should be digits
        else:
            if char in similar_char_to_int.keys():
                improved_text += similar_char_to_int[char]
            else:
                improved_text += char
    
    return improved_text

def adjust_gamma(image, gamma=1.5):
    """Adjust image gamma for better contrast"""
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)
