import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import os
import tool

# Add model path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)
import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf
from handGestureRecognition import handGestureRecognitionWidget

class handGesturePracticeToolWidget(QWidget):
    def __init__(self, gesture_names, effect_name,  parent=None):
        super().__init__(parent)
        
        self.currentGesture_idx = 0
        self.gesture_names = gesture_names
        self.duration = 0
        self.parent_widget = parent
        self.effect = effect_name
        self.effect_length = tool.get_effect_frame_length(self.effect)
        self.png_num = 1
        self.finish_practice = False
        # Layout setup
        main_layout = QVBoxLayout()
        
        # Timer widget
        self.timerLabel = QLabel("00:00")
        main_layout.addWidget(self.timerLabel, alignment=Qt.AlignCenter)

        # Add webcam feed
        self.video_frame = tool.create_webcam_widget("Let's practice!")
        main_layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)

        # Gesture images layout
        self.gesture_layout = QHBoxLayout()
        self.gesture_layout.setSpacing(0)  # Set spacing to 0
        self.gesture_layout.setContentsMargins(0, 0, 0, 0)
        for gesture_name in gesture_names:
            img = f'images/handGestureBtn/{gesture_name}Btn.png'
            pixmap = QPixmap(img).scaled(150, 150, Qt.KeepAspectRatio)
            gesture_icon = QLabel()
            gesture_icon.setPixmap(pixmap)
            gesture_icon.setAlignment(Qt.AlignCenter)
            gesture_icon.setFixedSize(150, 150)
            self.gesture_layout.addWidget(gesture_icon)
        self.gesture_layout.addStretch(1)
        main_layout.addLayout(self.gesture_layout)
        
        # button layout
        bottom_layout = QHBoxLayout()
         # Add Start Button
        self.startBtn = QPushButton(f"Start!")
        self.startBtn.setContentsMargins(0, 0, 0, 0)
        self.startBtn.setFixedSize(100, 50)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.setStyleSheet("background-color: green; border: none; font: 15px; color: white;")
        self.startBtn.clicked.connect(self.toggleStart)
        bottom_layout.addWidget(self.startBtn, alignment=Qt.AlignLeft)
        
        # add label for comment
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 20px;")
        bottom_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        # Add Close Button
        self.stopBtn = QPushButton("Stop")
        self.stopBtn.setContentsMargins(0, 0, 0, 0)
        self.stopBtn.setFixedSize(100, 50)
        self.stopBtn.setCursor(Qt.PointingHandCursor)
        self.stopBtn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.stopBtn.clicked.connect(self.toggleStop)
        bottom_layout.addWidget(self.stopBtn, alignment=Qt.AlignRight)
        
        
         # Add Close Button
        self.closeBtn = QPushButton("Close")
        self.closeBtn.setContentsMargins(0, 0, 0, 0)
        self.closeBtn.setFixedSize(100, 50)
        self.closeBtn.setCursor(Qt.PointingHandCursor)
        self.closeBtn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.closeBtn.clicked.connect(self.toggleClose)
        bottom_layout.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        
    def toggleStart(self):
        self.startBtn.hide()
        self.start_timer()
        self.recognitionTask()
        
    def toggleStop(self):
        self.stop_timer()
    
    def toggleClose(self):
        self.toggleStop()
        self.backToMain()
        
    def start_timer(self):
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.update_timer)
        self.clock.start(1000)
        
    def update_timer(self):
        self.duration += 1
        minutes = self.duration // 60
        seconds = self.duration % 60
        self.timerLabel.setText(f"{minutes:02}:{seconds:02}")
    
    def stop_timer(self):
        self.clock.stop()
        self.release_webcam()
        
    def recognitionTask(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        self.timer.start(100)  
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame = cv2.flip(frame, 1)
            if self.finish_practice == False:
                self.status, q_img = tool.recognize_hand_gesture(self.gesture_names[self.currentGesture_idx],  frame)
                if self.status == True:
                    if self.currentGesture_idx != len(self.gesture_names) - 1:
                        self.currentGesture_idx += 1
                        self.status_label.setText(f"Correct! Next gesture: {self.gesture_names[self.currentGesture_idx]}")
                        self.status_label.setStyleSheet("color: green;")
                    else:
                        self.finish_practice = True
                        self.clock.stop()
                        self.finishPractice()
            else:
                if self.effect and  self.png_num <= self.effect_length:
                    q_img = self.play_effect(frame)
                    self.png_num += 1
                else:
                    height, width, channel = frame.shape
                    bytesPerLine = 3 * width
                    q_img = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                        
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))

    def finishPractice(self):
        self.status_label.setText("You finish practice all selected gesture!")
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
    
    def play_effect(self, frame):
        frame = tool.add_gif2frame(self.effect, frame ,self.png_num)
        return frame
        
        
    def backToMain(self):
        self.release_webcam()
        self.parent_widget.navigate_to_main_widget()
        self.close()
    
    def release_webcam(self):
        if self.cap.isOpened():
            self.cap.release()

       

    

