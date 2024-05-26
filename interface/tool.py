# handGestureData.py
import json
import os
import sys
# Calculate the absolute path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)
import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import numpy


# variable
target_size = (224, 224)
model = tf.keras.models.load_model("Model/color_fps4_hand_splited_dataset.h5")
frameWidth = 1280/1.2
frameHeight = 720/1.2
label_x, label_y = int(frameWidth//2), 50
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
    
     # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True,min_detection_confidence=0.3,  min_tracking_confidence=0.3, max_num_hands=2)
    mp_drawing = mp.solutions.drawing_utils
    # Convert the BGR image to RGB and process it with MediaPipe Hands
    processed_image = utils.image_processing(target_size, imageShow, False)
    # exist, hand_area_coordinates = utils.find_hand_region(imageShow)  # return the hand area coordinates
    
    results = hands.process(processed_image)
    exist = results.multi_hand_landmarks is not None and  len(results.multi_hand_landmarks) == 2
    if exist:
        # hand keypoint
        
        # Get the bounding box coordinates
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(imageShow, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            x_min = min(landmark.x for landmark in hand_landmarks.landmark)
            x_max = max(landmark.x for landmark in hand_landmarks.landmark)
            y_min = min(landmark.y for landmark in hand_landmarks.landmark)
            y_max = max(landmark.y for landmark in hand_landmarks.landmark)
        # Convert the coordinates to pixels
            height, width, _ = imageShow.shape
            cx, cy, cw, ch = int(x_min * width), int(y_min * height), int((x_max - x_min) * width), int((y_max - y_min) * height)
            hand_area_coordinates = (cx, cy, cw, ch) 
        
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