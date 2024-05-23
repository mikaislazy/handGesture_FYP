from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QTimer
import cv2
import os
import sys

# Calculate the absolute path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)

import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf

class handGestureRecognitionWidget(QWidget):
    def __init__(self, gesture_name, parent=None):
        super().__init__(parent)
        
        self.parent_widget = parent
        
        # Hand gesture recognition setup
        self.LENIENCY = 100
        self.target_size = (224, 224)
        mpHands = mp.solutions.hands
        self.hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.1, min_tracking_confidence=0.1)
        mpDraw = mp.solutions.drawing_utils
        self.model = tf.keras.models.load_model("Model/color_fps4_hand_splited_dataset.h5")
        
        # Layout
        self.layout = QVBoxLayout(self)
        button_layout = QHBoxLayout(self)
        
        if not gesture_name:
            gesture_name = 'Testing'
        
        # Add webcam feed
        self.video_frame = QLabel(f"{gesture_name} Recognition Task")
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setFixedWidth(640*1.2)
        self.video_frame.setFixedHeight(480*1.2)
        self.video_frame.setAlignment(Qt.AlignCenter)
        self.video_frame.setStyleSheet("font: 15px;")
        self.layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)
        # self.layout.addStretch()
        
        # Add Start Button
        self.startBtn = QPushButton(f"Start!")
        self.startBtn.setContentsMargins(0, 0, 0, 0)
        self.startBtn.setFixedSize(100, 50)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.setStyleSheet("background-color: green; border: none; font: 15px; color: white;")
        self.startBtn.clicked.connect(self.toggleStart)
        button_layout.addWidget(self.startBtn, alignment=Qt.AlignLeft)
        # self.layout.addWidget(self.startBtn, alignment=Qt.AlignLeft)
        
        # Add Close Button
        self.closeBtn = QPushButton("Close")
        self.closeBtn.setContentsMargins(0, 0, 0, 0)
        self.closeBtn.setFixedSize(100, 50)
        self.closeBtn.setCursor(Qt.PointingHandCursor)
        self.closeBtn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.closeBtn.clicked.connect(self.backToMain)
        button_layout.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        # self.layout.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        
        self.layout.addLayout(button_layout)
    
    def recognize_hand_gesture(self, frame):
        imageShow = frame.copy()
        results = self.hands.process(frame)

        if results.multi_hand_landmarks:
            xs = []
            ys = []
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xs.append(cx)
                    ys.append(cy)
                if len(xs) and len(ys):
                    ma_x = max([0, max(xs) + self.LENIENCY])
                    ma_y = max([0, max(ys) + self.LENIENCY])
                    mi_x = max([0, min(xs) - self.LENIENCY])
                    mi_y = max([0, min(ys) - self.LENIENCY])
                    cropped = frame[mi_y:ma_y, mi_x:ma_x]
                    image = utils.image_processing(self.target_size, cropped, True)
                    tf_img = tf.image.convert_image_dtype(image, tf.dtypes.uint8)
                    x = tf.expand_dims(image, 0)
                    pred = self.model.predict(x)[0]
                    labels = ['ChanDingYin', 'HuoYanYin', 'MiTuoDingYin', 'Retsu', 'Rin', 'TaiJiYin', 'Zai', 'Zen', 'ZhiJiXiangYin']
                    class_indices = {i: labels[i] for i in range(len(labels))}
                    exist, area = utils.find_hand_region(imageShow)
                    if exist:
                        cx, cy, cw, ch = area
                        cv2.putText(imageShow, utils.show_pred_max_toString(pred, class_indices), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        imageShow = cv2.rectangle(imageShow, pt1=(cx, cy), pt2=(cx+cw, cy+ch), color=(245, 66, 108), thickness=2)
            imageShow = cv2.cvtColor(imageShow, cv2.COLOR_RGB2BGR)
            height, width, channel = imageShow.shape
            bytesPerLine = 3 * width
            qImg = QImage(imageShow.data, width, height, bytesPerLine, QImage.Format_RGB888)
            return qImg
    
    def toggleStart(self):
        self.startBtn.hide()
        self.recognitionTask()
    
    def recognitionTask(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        self.timer.start(20)  # Update the frame every 20 ms

        # Label for status and result
        self.status_label = QLabel("Hand Gesture Correct!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
        self.layout.addWidget(self.status_label)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            # q_img = self.recognize_hand_gesture(frame)
            # self.video_frame.setPixmap(QPixmap.fromImage(q_img))
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.video_frame.setPixmap(QPixmap.fromImage(qImg))
    
    def correctGesture(self):
        self.status_label = QLabel("Hand Gesture Correct!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
        self.layout.addWidget(self.status_label)
    
    def backToMain(self):
        self.parent_widget.navigate_to_main_widget()
        self.close()