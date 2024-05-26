from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QTimer
import cv2
import os
import sys
import tool
import numpy 

# Calculate the absolute path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)

import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf

class handGestureRecognitionWidget(QWidget):
    def __init__(self, gesture_name, insert_record_task2_callback , parent=None):
        super().__init__(parent)
        
        self.parent_widget = parent
        self.insert_record_task2_callback = insert_record_task2_callback
        
        # Hand gesture recognition setup
        self.LENIENCY = 100
        self.target_size = (224, 224)
        mpHands = mp.solutions.hands
        self.hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.1, min_tracking_confidence=0.1)
        mpDraw = mp.solutions.drawing_utils
        self.model = tf.keras.models.load_model("Model/color_fps4_hand_splited_dataset.h5")
        
        self.gesture_name = gesture_name
        self.status = False
        self.duration = 60
        # Layout
        self.layout = QVBoxLayout(self)
        bottom_layout = QHBoxLayout(self)
        
        # time Label
        self.timerLabel = QtWidgets.QLabel("01:00")
        self.layout.addWidget(self.timerLabel, alignment=Qt.AlignCenter)
        
        # Add webcam feed
        video_frame_title = f"{gesture_name} Recognition Task"
        self.video_frame = tool.create_webcam_widget(video_frame_title)
        self.layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)
        # self.layout.addStretch()
        
        # Add Start Button
        self.startBtn = QPushButton(f"Start!")
        self.startBtn.setContentsMargins(0, 0, 0, 0)
        self.startBtn.setFixedSize(100, 50)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.setStyleSheet("background-color: green; border: none; font: 15px; color: white;")
        self.startBtn.clicked.connect(self.toggleStart)
        bottom_layout.addWidget(self.startBtn, alignment=Qt.AlignLeft)
        # self.layout.addWidget(self.startBtn, alignment=Qt.AlignLeft)
        
        # add label for comment
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 20px;")
        bottom_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        # Add Close Button
        self.closeBtn = QPushButton("Close")
        self.closeBtn.setContentsMargins(0, 0, 0, 0)
        self.closeBtn.setFixedSize(100, 50)
        self.closeBtn.setCursor(Qt.PointingHandCursor)
        self.closeBtn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.closeBtn.clicked.connect(self.backToMain)
        bottom_layout.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        self.closeBtn.hide() # hide before the task is finished
        
        self.layout.addLayout(bottom_layout)
    
    
    
    def toggleStart(self):
        self.startBtn.hide()
        self.start_timer()
        self.recognitionTask()
    
    def start_timer(self):
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.update_timer)
        self.clock.start(1000)
    
    def update_timer(self):
        self.duration -= 1
        if self.duration == 0:
            self.clock.stop()
            self.release_webcam()
            self.fail_task()
            self.closeBtn.show()
        else:
            minutes = self.duration // 60
            seconds = self.duration % 60
            self.timerLabel.setText(f"{minutes:02}:{seconds:02}")
        
    def recognitionTask(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        self.timer.start(300) 

       
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame = cv2.flip(frame, 1)
            self.status, q_img = tool.recognize_hand_gesture(self.gesture_name,  frame)
            self.show_gesture_comment(self.status)
            if self.status:
                # end the task
                self.release_webcam()
                self.closeBtn.show()
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))
    
    def show_gesture_comment(self, status):
        if status is None:
                self.show_hand_absence_alert()
        elif status == True:
            self.correctGesture()
        else:
            self.wrongGesture()
            
    def correctGesture(self):
        self.status_label.setText("Correct Gesture!")
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
    
    def wrongGesture(self):
        self.status_label.setText("Wrong Gesture!")
        self.status_label.setStyleSheet("font-size: 20px; color: red;")
        
    def show_hand_absence_alert(self):
        self.status_label.setText("No hand detected!")
        self.status_label.setStyleSheet("font-size: 20px; color: red;")
    
    def fail_task(self):
        self.status_label.setText("Task Failed!")
        self.status_label.setStyleSheet("font-size: 20px; color: red;")
        
    def backToMain(self):
        if self.status:
            time = 60 - self.duration
        else:
            time = 60
        self.insert_record_task2_callback(self.gesture_name, self.status, time)
        self.release_webcam()
        self.close()
        self.parent_widget.navigate_to_main_widget()
    
    def release_webcam(self):
        if self.cap.isOpened():
            self.cap.release()

# Main application to run the widget
def main():
    app = QApplication([])
    gesture_name = 'gesture1'  # Example gesture name
    widget = handGestureRecognitionWidget(gesture_name)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
