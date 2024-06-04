from pathlib import Path
import numpy as np
import json
import os
import cv2
import mediapipe as mp
from gesture_constants import GESTURES_INDICS
from Model.VGGModel  import VGGModel 
import Keypoint.analyse_keypoint_utils as keypoints_utils
# the color format of the frame is RGB

# variable
model = VGGModel()
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=25, detectShadows=True)


def count_jpgs(path):
    return len(list(path.rglob('*.jpg')))

def mkdir(path):
    if not path.exists():
        path.mkdir()
        print('{} created'.format(path))
    else:
        print('{} already exists'.format(path))


def save_confg(indices, input_size, fp):
    '''
    Arguments
    indic - dict
    fp - file path
    '''
    config = {
        'indices': indices,
        'input_size': input_size
    }
    with open(fp, 'w', encoding='UTF-8') as f:
        json.dump(config, f,ensure_ascii=False)

def image_processing(target_size, img, hand_area_only):
    """ image processing - resize the image to 224 * 224 , then apply median filter and gaussian filter. Finally, apply auto contrast adjustment to the images

    Args:
        target_size (int, int): input =( width, height)
        img (np_array): input image
        hand_area_only ( boolean ): True/False - determine whether to crop the hand area only or not
    """
    # crap the hand regions
    if hand_area_only:
        getFlag, img= crop_hand_area(img)
        if not getFlag:
            return None
    # image processing
    # apply median filter to image
    filteredImg = cv2.medianBlur(img, ksize=3)
    # apply gaussian filter to image
    gaussBlurImg = cv2.GaussianBlur(filteredImg,(3,3),0)
    # automatic contrast adjustment
    adjustedImg = auto_contrast_adjustment(gaussBlurImg, 255, 0)
    # convert image to grayscale
    # grayImg = cv2.cvtColor(adjustedImg, cv2.COLOR_BGR2GRAY)
    # apply binary thresholding to image
    # ret, threshImg = cv2.threshold(grayImg,160,255,cv2.THRESH_BINARY)
    # apply canny edge detection to image
    # cannyImg = cv2.Canny(threshImg,10,100)
    # resize the image to target size
    resizedImg = cv2.resize(adjustedImg, target_size)
    return resizedImg

def auto_contrast_adjustment(img, max_val, min_val):
    image = img.copy()

    low, high = image.min(), image.max()

    image = min_val + (image - low) * ((max_val - min_val) / (high - low))

    return image.astype(np.uint8) # for canny edge detection

def crop_hand_area(img, adj_x = 0, adj_y = 0, adj_w = 0, adj_h = 0):
    """ crop the hand area only

    Args:
        img (np_array): input image
        adj_x (int): number of pixel to shift horizontally
        ady_y (int): number of pixel to shift vertically
    Returns:
        img (np_array): output image
    """
    b, g, r = cv2.split(img)
    # Create a binary mask based on the skin rgb color 
    skin_mask = np.logical_and.reduce((r > 85, r - b > 10, r - g > 10)).astype(np.uint8) * 255
    
    # Find the largest skin part ( i.e. hand region)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
    if len(contours) > 0:
        # Find the largest contour (hand)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        #adjust cropped hand region
        w += adj_w
        h += adj_h
        x += adj_x
        y += adj_y
        cropped_image = img[y:y+h, x:x+w]
        return True, cropped_image
    
    return False, None
def find_hand_region(img, adj_x = 0, adj_y = 0, adj_w = 0, adj_h = 0):
    """ crop the hand area only

    Args:
        img (np_array): input image
        adj_x (int): number of pixel to shift horizontally
        ady_y (int): number of pixel to shift vertically
    Returns:
        img (np_array): output image
    """
    b, g, r = cv2.split(img)
    # Create a binary mask based on the skin rgb color 
    skin_mask = np.logical_and.reduce((r > 85, r - b > 10, r - g > 10)).astype(np.uint8) * 255
    
    # Find the largest skin part ( i.e. hand region)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
    if len(contours) > 0:
        # Find the largest contour (hand)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        #adjust cropped hand region
        w += adj_w
        h +=adj_h
        x += adj_x
        y += adj_y
        return True, [x, y, w, h]
    
    return False, None

def hand_segmentation_MOG(frame):
    # Apply background subtraction
    fg_mask = bg_subtractor.apply(frame)
    
    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    
    # Apply skin color mask
    skin_mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)
    
    # Combine foreground mask and skin color mask
    combined_mask = cv2.bitwise_and(fg_mask, skin_mask)
    
    # Find contours
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        # Calculate the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        # Draw the bounding rectangle on the original frame
        return True,[x, y, w, h]
    return False, None

def hand_segmentation_Mediapipe(frame):
    frame = frame.copy()
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True,min_detection_confidence=0.3,  min_tracking_confidence=0.3, max_num_hands=2)
    # mp_drawing = mp.solutions.drawing_utils
    # process the hand
    results = hands.process(frame)
    exist = results.multi_hand_landmarks is not None # 2 hand detected
    if exist:
        # hand keypoints
        x_min = y_min = float('inf')
        x_max = y_max = float('-inf')

        for hand_landmarks in results.multi_hand_landmarks:
            x_min = min(x_min, min(landmark.x for landmark in hand_landmarks.landmark))
            x_max = max(x_max, max(landmark.x for landmark in hand_landmarks.landmark))
            y_min = min(y_min, min(landmark.y for landmark in hand_landmarks.landmark))
            y_max = max(y_max, max(landmark.y for landmark in hand_landmarks.landmark))

        # Convert the coordinates to pixels
        height, width, _ = frame.shape
        cx, cy, cw, ch = int(x_min * width), int(y_min * height), int((x_max - x_min) * width), int((y_max - y_min) * height)
        hand_area_coordinates = [cx, cy, cw, ch]
        
        return True, hand_area_coordinates
    return False, None

def hand_segmentation_Skin(frame):
    frame = frame.copy()
    
    # Applying Bilateral Filter
    frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Converting from BGR to HSV color space
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    HSV_mask = cv2.inRange(frame_HSV, (0, 30, 60), (20, 150, 255))
    HSV_mask = cv2.medianBlur(HSV_mask, 5)

    # Converting from BGR to YCbCr color space
    frame_YCrCb = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
    YCrCb_mask = cv2.inRange(frame_YCrCb, (0, 133, 77), (235, 173, 127))
    YCrCb_mask = cv2.medianBlur(YCrCb_mask, 5)

    # Merge skin detection (YCbCr and HSV)
    global_mask = cv2.bitwise_and(YCrCb_mask, HSV_mask)
    global_mask = cv2.medianBlur(global_mask, 5)
    global_mask = cv2.morphologyEx(global_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    # Find contours in the mask
    contours, _ = cv2.findContours(global_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If at least one contour was found
    if contours:
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the coordinates of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Check if the contour meets the defined thresholds
        if  check_contour(largest_contour, 10000, 1000, 30, 30):
            return True, [x, y, w+200, h+200]


    return False, None
def check_contour(contour, max_area_threshold, min_area_threshold, width_threshold, height_threshold):
    # Calculate the area, width, and height of the contour
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    # Check if the contour meets the defined thresholds
    if area < max_area_threshold and area > min_area_threshold and w > width_threshold and h > height_threshold:
        return True
    return False

    
def recognize_hand_gesture(gesture_name ,frame, is_draw_feedback):
    status = False
    imageShow = frame.copy()
    prediction = None
    # set the method for hand segmentation to check whether someone is here
    exist2, hand_area_coordinates2 = hand_segmentation_Mediapipe(imageShow) # check hand really exist
    exist1, hand_area_coordinates1 = hand_segmentation_Skin(imageShow) # function is set for the situation that mediapipe fail to detect the hand


    if exist1 or exist2:
        # cx, cy, cw, ch = hand_area_coordinates2 if exist2 else hand_area_coordinates1
        cx, cy, cw, ch =  hand_area_coordinates1 if exist1 else hand_area_coordinates2
        all_pred, prediction, prediction_percentage = model.get_max_prediction(imageShow)
        prediction_text = f"{prediction}: {prediction_percentage:.2f}%"
        # cv2.putText(imageShow,prediction_text, (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        # if exist2:
        imageShow = cv2.rectangle(img=imageShow, pt1=(cx, cy), pt2=(cx+cw, cy+ch), color=(245, 66, 108), thickness=2)
        if prediction == gesture_name and prediction_percentage >= 0.9:
            status = True
        else:
            status = False
            if is_draw_feedback:
                imageShow = keypoints_utils.analyse_keypoints(imageShow, gesture_name)
    else:
        status = None
        
    return status, imageShow, prediction
