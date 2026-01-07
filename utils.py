import string
import easyocr
import cv2
import numpy as np


reader = easyocr.Reader(['en'], gpu=False)


#dictionaries to convert similar characters to numbers and viceversa
#to improve the OCR results
similar_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

similar_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}





def get_car (plate_coordinates, vehicle_ids):
    
    x1, y1, x2, y2 = plate_coordinates
    
    #iterate every vehicle detected in the frame
    #in search for the vehicle that contains the plate
    #by checking if the center of the plate is inside the vehicle box
    for i, vehicle in enumerate(vehicle_ids):
        #get the coordinates of the vehicle
        xcar1, ycar1, xcar2, ycar2, vehicle_id = vehicle
        
        #check if the center of the plate is inside the vehicle box
        if x1 > xcar1 and x2 < xcar2 and y1 > ycar1 and y2 < ycar2:
            #return the coordinates of the vehicle + vehicle_id
            return vehicle
    
    
    
    
    #if no vehicle found return -1
    return -1, -1, -1, -1, -1



def read_plate(plate_image):
    
    results = reader.readtext(plate_image)
    
    for result in results:
        bounding_box, plate_text, plate_score = result
        
        #clean the text read
        plate_text = plate_text.upper().replace(" ", "")
        
        #check if the plate format is valid --> italian plate format
        if plate_format_check(plate_text):
            return improve_plate_text(plate_text), plate_score
        
        return improve_plate_text(plate_text), plate_score
    
    #return the text read, and confidence (score)
    return None, 0.0




def plate_format_check(plate_text):
    #check if the plate format is valid
    #it uses the common italian plate format
    
    if len(plate_text) != 7:
        return False
    
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    
    #first two characters must be letters
    if plate_text[0] not in string.ascii_uppercase and plate_text[0] not in similar_int_to_char.keys():
        return False
    
    if plate_text[1] not in string.ascii_uppercase and plate_text[1] not in similar_int_to_char.keys():
        return False
    
    #third, fourth and fifth characters must be digits
    if plate_text[2] not in digits and plate_text[2] not in similar_char_to_int.keys():
        return False
    
    if plate_text[3] not in digits and plate_text[3] not in similar_char_to_int.keys():
        return False
    if plate_text[4] not in digits and plate_text[4] not in similar_char_to_int.keys():
        return False
    
    #last two characters must be letters
    if plate_text[5] not in string.ascii_uppercase and plate_text[5] not in similar_int_to_char.keys():
        return False
    if plate_text[6] not in string.ascii_uppercase and plate_text[6] not in similar_int_to_char.keys():
        return False
    
    return True


def improve_plate_text(plate_text):
    #improve the plate text read by converting similar characters to numbers and viceversa
    improved_text = ""
    
    for i, char in enumerate(plate_text):
        #if the position of the charachter is a letter
        #verify that easyocr has not read a number instead
        #and convert it to the corresponding letter
        if i in [0,1,5,6]:
            if char in similar_int_to_char.keys():
                improved_text += similar_int_to_char[char]
            else:
                improved_text += char
        #viceversa for the digits
        else:
            if char in similar_char_to_int.keys():
                improved_text += similar_char_to_int[char]
            else:
                improved_text += char
    
    return improved_text


def adjust_gamma(image, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)