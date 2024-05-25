from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QTimer
import cv2
import os
import sys
from tool import GESTURES, GESTURES_INDICS
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
        self.duration = 5
        # Layout
        self.layout = QVBoxLayout(self)
        bottom_layout = QHBoxLayout(self)
        
        # time Label
        self.timerLabel = QtWidgets.QLabel("01:00")
        self.layout.addWidget(self.timerLabel, alignment=Qt.AlignCenter)
        
        # Add webcam feed
        self.frameWidth = 1280/1.2
        self.frameHeight = 720/1.2
        self.video_frame = QLabel(f"{gesture_name} Recognition Task")
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setFixedWidth(self.frameWidth)
        self.video_frame.setFixedHeight(self.frameHeight)
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
    
    def recognize_hand_gesture(self, frame):
        imageShow = frame.copy()
        processed_hand_image = utils.image_processing(self.target_size, imageShow, True)
        exist, hand_area_coordinates = utils.find_hand_region(imageShow)  # return the hand area coordinates
        if exist:
            x = tf.expand_dims(processed_hand_image, 0)
            pred = self.model.predict(x)[0]
            cx, cy, cw, ch = hand_area_coordinates
            prediction = GESTURES_INDICS[pred.argmax()]
            prediction_text = utils.show_pred_max_toString(pred, GESTURES_INDICS)
            cv2.putText(imageShow,prediction_text, (int(self.frameWidth//2), 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            imageShow = cv2.rectangle(img=imageShow, pt1=(cx, cy), pt2=(cx+cw, cy+ch), color=(245, 66, 108), thickness=2)
            if prediction == self.gesture_name:
                self.status = True
                self.correctGesture()
                # end the task
                self.release_webcam()
                self.closeBtn.show()
        else:
            self.show_hand_absence_alert()
            
        height, width, channel = imageShow.shape
        bytesPerLine = 3 * width
        qImg = QImage(imageShow.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg
    
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
        self.timer.start(500)  # Update the frame every 20 ms

        # # Label for status and result
        # self.status_label = QLabel("")
        # self.status_label.setAlignment(Qt.AlignCenter)
        # self.status_label.setStyleSheet("font-size: 20px; color: green;")
        # self.layout.addWidget(self.status_label)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame = cv2.flip(frame, 1)
            q_img = self.recognize_hand_gesture(frame)
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))
    
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
