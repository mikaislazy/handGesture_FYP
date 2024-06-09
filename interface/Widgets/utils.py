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

def hand_segmentation_Mediapipe(frame):
    frame = frame.copy()
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True,min_detection_confidence=0.3,  min_tracking_confidence=0.3, max_num_hands=2)

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

    
    # Converting from RGB to HSV color space
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    HSV_mask = cv2.inRange(frame_HSV, (0, 58, 0), (50, 173, 255))
    # HSV_mask = cv2.medianBlur(HSV_mask, 5)

    # Converting from RGB to YCbCr color space
    frame_YCrCb = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
    YCrCb_mask = cv2.inRange(frame_YCrCb, (0, 135, 85), (255, 180, 135))
    # YCrCb_mask = cv2.medianBlur(YCrCb_mask, 5)

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
