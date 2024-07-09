from collections import deque
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QTimer
import cv2
import os
import sys
import  tool
import numpy 
import utils

abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)

import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf

class handGestureRecognitionWidget(QWidget):
    def __init__(self, gesture_name, insert_record_task2_callback , method, parent=None):
        super().__init__(parent)
        
        self.parent_widget = parent
        self.insert_record_task2_callback = insert_record_task2_callback
        
        # set the buffer
        self.buffer_size = 8  # Number of frames to consider for temporal smoothing
        self.prediction_buffer = deque(maxlen=self.buffer_size)
        self.draw_feedback = False
        # Open the default webcam
        self.cap = cv2.VideoCapture(0)
        
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
        video_frame_title = f"{gesture_name} Recognition Task:\n{method}"
        self.video_frame = tool.create_webcam_widget(video_frame_title)
        self.video_frame.setWordWrap(True)
        self.layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)
        
        # Add Start Button
        self.start_btn = QPushButton(f"Start!")
        self.start_btn.setContentsMargins(0, 0, 0, 0)
        self.start_btn.setFixedSize(100, 50)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("background-color: green; border: none; font: 15px; color: white;")
        self.start_btn.clicked.connect(self.toggle_start)
        bottom_layout.addWidget(self.start_btn, alignment=Qt.AlignLeft)
        
        # add label for comment
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 20px;")
        bottom_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        # Add Close Button
        self.close_btn = QPushButton("Close")
        self.close_btn.setContentsMargins(0, 0, 0, 0)
        self.close_btn.setFixedSize(100, 50)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.close_btn.clicked.connect(self.back_to_main)
        bottom_layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
        self.close_btn.hide() # hide before the task is finished
        
        self.layout.addLayout(bottom_layout)
    
    
    
    def toggle_start(self):
        self.start_btn.hide()
        self.start_timer()
        self.recognition_task()
    
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
            self.close_btn.show()
        else:
            minutes = self.duration // 60
            seconds = self.duration % 60
            self.timerLabel.setText(f"{minutes:02}:{seconds:02}")
        
    def recognition_task(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        self.timer.start(100) 

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            self.status, imgShow, prediction = utils.recognize_hand_gesture(self.gesture_name,  frame, self.draw_feedback)
            # only draw feedback when buffer is full
            if self.draw_feedback: 
                self.draw_feedback = False
            self.prediction_buffer.append(prediction)
            prediction_count = self.prediction_buffer.count(self.gesture_name)
            self.show_gesture_comment(self.status)
            
            if self.status == True and prediction_count >= 4 :
                self.prediction_buffer.clear()
                # end the task
                self.release_webcam()
                self.close_btn.show()
             # if buffer is half full -> draw feedback
            if len(self.prediction_buffer) == self.buffer_size//2:
                self.draw_feedback = True
            # if buffer is full -> clear the buffer
            if len(self.prediction_buffer) == self.buffer_size:
                self.prediction_buffer.clear()  # Clear the buffer after processing
            q_img = tool.frame2QImg(imgShow)
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))
    
    def show_gesture_comment(self, status):
        def correct_gesture(self):
            self.status_label.setText("Correct Gesture!")
            self.status_label.setStyleSheet("font-size: 20px; color: green;")
        
        def wrong_gesture(self):
            self.status_label.setText("Wrong Gesture!")
            self.status_label.setStyleSheet("font-size: 20px; color: red;")
            
        def show_hand_absence_alert(self):
            self.status_label.setText("No hand detected!")
            self.status_label.setStyleSheet("font-size: 20px; color: red;")
            
        if status is None:
            show_hand_absence_alert(self)
        elif status == True:
            correct_gesture(self)
        else:
            wrong_gesture(self)
            
    
    def fail_task(self):
        self.status_label.setText("Task Failed!")
        self.status_label.setStyleSheet("font-size: 20px; color: red;")
        
    def back_to_main(self):
        if self.status:
            time = 60 - self.duration
        else:
            time = 60
        if not self.status: self.status = False
        self.insert_record_task2_callback(self.gesture_name, self.status, time)
        self.release_webcam()
        self.close()
        if self.parent_widget:
            self.parent_widget.navigate_to_main_widget()
    
    def release_webcam(self):
        if self.cap.isOpened():
            self.cap.release()

