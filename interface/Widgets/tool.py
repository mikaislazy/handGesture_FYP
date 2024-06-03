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
from gesture_constants import GESTURES_INDICS

current_dir = os.path.dirname(os.path.abspath(__file__))

# variable

frameWidth = 1280/1.2
frameHeight = 720/1.2
label_x, label_y = int(frameWidth//2), 50


# Define the lower and upper boundaries of the HSV values for skin color
lower_hsv = np.array([0, 48, 80], dtype=np.uint8)  # Adjusted for typical skin detection
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


def create_webcam_widget(title):
    
    video_frame = QLabel(f"{title}")
    video_frame.setFrameShape(QFrame.Box)
    video_frame.setFixedWidth(frameWidth)
    video_frame.setFixedHeight(frameHeight)
    video_frame.setStyleSheet("font: 15px;")
    return video_frame


def add_gif2frame(effect_name, frame, png_num):
    effect_frame_path = get_effect_frame_path(effect_name)
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
        effect_frame_path = get_effect_frame_path(effect_name)
        effect_frame_length = len(os.listdir(effect_frame_path)) 

    return effect_frame_length

def get_effect_frame_path(effect_name):
    effect_frame_path = f"other/frames/{effect_name}"
    return  os.path.join(current_dir, effect_frame_path )

def frame2QImg(frame):
    height, width, channel = frame.shape
    bytesPerLine = 3 * width
    qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return qImg