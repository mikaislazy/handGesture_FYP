# handGestureData.py
import json
import os
import sys
import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import numpy

# Get the parent directory
# parent_dir = os.path.dirname( os.getcwd())
# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model file
model_path = os.path.join(current_dir, '../Model/color_fps4_splited_dataset.h5')
print('model_path:',model_path)

# variable
target_size = (224, 224)
model = tf.keras.models.load_model(model_path)
frameWidth = 1280/1.2
frameHeight = 720/1.2
label_x, label_y = int(frameWidth//2), 50

# Initialize the background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=25, detectShadows=True)

# Define the lower and upper boundaries of the HSV values for skin color
lower_hsv = np.array([0, 20, 70], dtype=np.uint8)
upper_hsv = np.array([20, 255, 255], dtype=np.uint8)

def load_question(gesture_name, json_file):
    questions = []
    options = []
    with open(json_file, 'r') as f:
        question_bank = json.load(f)
        q_opt = question_bank[gesture_name]["questions"]
        for task in q_opt:
            questions.append(task['question'])
            options.append(task['options'])
    return questions, options

def load_answer(gesture_name, json_file):
    answers = []
    with open(json_file, 'r') as f:
        answers_bank = json.load(f)
        q_a = answers_bank[gesture_name]["answers"]
        for ans in q_a:
            answers.append(ans["correct_option"])
    return answers

def recognize_hand_gesture(gesture_name ,frame):
    status = False
    imageShow = frame.copy()
    
    #  # Initialize MediaPipe Hands
    # mp_hands = mp.solutions.hands
    # hands = mp_hands.Hands(static_image_mode=True,min_detection_confidence=0.3,  min_tracking_confidence=0.3, max_num_hands=2)
    # mp_drawing = mp.solutions.drawing_utils
    # # Convert the BGR image to RGB and process it with MediaPipe Hands
    exist, hand_area_coordinates = hand_segmentation(imageShow)
    # # exist, hand_area_coordinates = utils.find_hand_region(imageShow)  # return the hand area coordinates
    
    # results = hands.process(processed_image)
    # exist = results.multi_hand_landmarks is not None and  len(results.multi_hand_landmarks) == 2
    
    if exist:
        x, y, w, h = hand_area_coordinates
        input_img = imageShow[y:y+h, x:x+w] # hand area
        processed_image = utils.image_processing(target_size, imageShow, False)
    #     # hand keypoint
        
    #     # Get the bounding box coordinates
    #     for hand_landmarks in results.multi_hand_landmarks:
    #         mp_drawing.draw_landmarks(imageShow, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    #         x_min = min(landmark.x for landmark in hand_landmarks.landmark)
    #         x_max = max(landmark.x for landmark in hand_landmarks.landmark)
    #         y_min = min(landmark.y for landmark in hand_landmarks.landmark)
    #         y_max = max(landmark.y for landmark in hand_landmarks.landmark)
    #     # Convert the coordinates to pixels
    #         height, width, _ = imageShow.shape
    #         cx, cy, cw, ch = int(x_min * width), int(y_min * height), int((x_max - x_min) * width), int((y_max - y_min) * height)
    #         hand_area_coordinates = (cx, cy, cw, ch) 
        
        x = tf.expand_dims(processed_image, 0)
        pred = model.predict(x)[0]
        cx, cy, cw, ch = hand_area_coordinates
        prediction = GESTURES_INDICS[pred.argmax()]
        prediction_percentage = pred[pred.argmax()]
        prediction_text = utils.show_pred_max_toString(pred, GESTURES_INDICS)
        cv2.putText(imageShow,prediction_text, (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        imageShow = cv2.rectangle(img=imageShow, pt1=(cx, cy), pt2=(cx+cw, cy+ch), color=(245, 66, 108), thickness=2)
        if prediction == gesture_name and prediction_percentage >= 0.9:
            status = True
            # self.correctGesture()
            # end the task
            # self.release_webcam()
            # self.closeBtn.show()
        else:
            status = False
    else:
        status = None
        # self.show_hand_absence_alert()
        
    height, width, channel = imageShow.shape
    bytesPerLine = 3 * width
    qImg = QImage(imageShow.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return status, qImg

def create_webcam_widget(title):
    
    video_frame = QLabel(f"{title}")
    video_frame.setFrameShape(QFrame.Box)
    video_frame.setFixedWidth(frameWidth)
    video_frame.setFixedHeight(frameHeight)
    video_frame.setStyleSheet("font: 15px;")
    return video_frame

def add_gif2frame(effect_name, frame, png_num):
    effect_frame_path = f"other/frames/{effect_name}"
    if os.path.exists(effect_frame_path):
        png_path = f"{effect_frame_path}/{effect_name}_{png_num}.png"
        pngimg = cv2.imread(png_path)
        frame = add_png2frame(frame, pngimg)
        
    else:
        print(f"Path {effect_frame_path} does not exist.")
    
    height, width, channel = frame.shape
    bytesPerLine = 3 * width
    return QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
    
def add_png2frame(frame, pngimg):
    rows1,cols1,channels1 = frame.shape
    pngimg = cv2.resize(pngimg, (cols1, rows1))
    pngimg = cv2.cvtColor(pngimg, cv2.COLOR_BGR2RGB)
   
    # get the background mask
    img2gray = cv2.cvtColor(pngimg,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask) # get the effect area in png

    # black-out the area of effect in frame
    img1_bg = cv2.bitwise_and(frame,frame,mask = mask_inv)

    # get the effect area in png
    img2_fg = cv2.bitwise_and(pngimg,pngimg,mask = mask)

    # combine frame and effect
    frame = cv2.add(img1_bg,img2_fg)
    

    return frame

  

def get_effect_frame_length( effect_name):
    if not effect_name:
        effect_frame_length = 0
    else:
        effect_frame_path = f"other/frames/{effect_name}"
        effect_frame_length = len(os.listdir(effect_frame_path)) 

    return effect_frame_length

def hand_segmentation(frame):
    # Apply background subtraction
    # frame = cv2.medianBlur(frame, 5)
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
    
GESTURES = [
    'HuoYanYin',
    'ChanDingYin',
    'MiTuoDingYin',
    'Retsu',
    'Rin',
    'Zai',
    'Zen',
    'ZhiJiXiangYin',
    'TaiJiYin'
]
GESTURES_INDICS = {0: 'ChanDingYin', 
                 1: 'HuoYanYin', 
                 2: 'MiTuoDingYin', 
                 3: 'Retsu', 
                 4: 'Rin', 
                 5: 'TaiJiYin', 
                 6: 'Zai', 
                 7: 'Zen', 
                 8: 'ZhiJiXiangYin'}
