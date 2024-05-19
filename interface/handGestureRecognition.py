import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QTimer
import cv2

class handGestureRecognitionWidget(QWidget):
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.start = False
        
        # Add webcam feed
        self.video_frame = QLabel()
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setFixedWidth(640*1.2)  # Set the width of the video frame
        self.video_frame.setFixedHeight(480*1.2)  # Set the height of the video frame
        self.layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)
        self.layout.addStretch()
        
        # add Start Button
        self.startBtn = QPushButton("Start")
        self.startBtn.setContentsMargins(0, 0, 0, 0)
        self.startBtn.setFixedSize(100, 50)  # Set the size of the buttons
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.setStyleSheet("background-color:green; border: none; font: 15px; color: white;")
        self.startBtn.clicked.connect(lambda checked: self.toggleStart())
        self.layout.addWidget(self.startBtn)
         
        
        # Timer to update the webcam feed
        # if self.start:
        #     self.timer = QTimer(self)
            
        #     self.timer.timeout.connect(self.update_frame)
            
        #     # Open the default webcam
        #     self.cap = cv2.VideoCapture(0)
        #     self.timer.start(20)  # Update the frame every 20 ms

        #     # Label for status and result
        #     self.status_label = QLabel("Hand Gesture Correct!")
        #     self.status_label.setAlignment(Qt.AlignCenter)
        #     self.status_label.setStyleSheet("font-size: 20px; color: green;")
        #     self.layout.addWidget(self.status_label)
            
    def toggleStart(self):
        self.start = True
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
            height, width, channel = frame.shape
            step = channel * width
            q_img = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))
    
    def correctGesture(self):
        self.status_label = QLabel("Hand Gesture Correct!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
        self.layout.addWidget(self.status_label)
    
    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()
    
        