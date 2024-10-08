from collections import deque
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import cv2
import os
import tool
import utils
# Add model path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)
import utils


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
        self.buffer_size = 8  # buffer size management
        self.prediction_buffer = deque(maxlen=self.buffer_size)
        self.draw_feedback = False
        self.cap = cv2.VideoCapture(0)
        
        # Layout setup
        layout = QVBoxLayout()
        
        # Timer widget
        self.timerLabel = QLabel("00:00")
        layout.addWidget(self.timerLabel, alignment=Qt.AlignCenter)

        # Add webcam feed
        self.video_frame = tool.create_webcam_widget("Let's practice!")
        layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)

        # Gesture images layout
        self.gesture_layout = QHBoxLayout()
        self.gesture_layout.setSpacing(0) 
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
        layout.addLayout(self.gesture_layout)
        
        # button layout
        bottom_layout = QHBoxLayout()
        # add Start Button
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
        
        self.comment_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 20px;")
        bottom_layout.addWidget(self.comment_label, alignment=Qt.AlignCenter)
        
        # add stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setContentsMargins(0, 0, 0, 0)
        self.stop_btn.setFixedSize(100, 50)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.stop_btn.clicked.connect(self.toggle_stop)
        self.stop_btn.hide()
        bottom_layout.addWidget(self.stop_btn, alignment=Qt.AlignRight)
        
        
         # add close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setContentsMargins(0, 0, 0, 0)
        self.close_btn.setFixedSize(100, 50)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("background-color: red; border: none; font: 15px; color: white;")
        self.close_btn.clicked.connect(self.toggle_close)
        bottom_layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
        
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        
    def toggle_start(self):
        # initialize the value for restart
        self.prediction_buffer.clear()
        self.draw_feedback = False
        self.png_num = 1
        self.finish_practice = False
        self.status_label.setText("")
        self.comment_label.setText("")
        self.currentGesture_idx = 0
        self.reopen_webcam()
        
        self.start_btn.hide()
        self.stop_btn.show()
        self.start_timer()
        self.recognition_task()
        
    def toggle_stop(self):
        self.start_btn.setText("Restart")
        self.status_label.setText("")
        self.comment_label.setText("")
        self.start_btn.show()
        self.stop_btn.hide()
        self.stop_timer()
    
    def toggle_close(self):
        self.toggle_stop()
        self.back_to_main()
        
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
        if hasattr(self, 'clock'):
            self.clock.stop()
        if hasattr(self, 'cap'):
            self.release_webcam()
        
    def recognition_task(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Open the default webcam
        self.timer.start(100)  
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            if self.finish_practice == False:
                status, imgShow, prediction = utils.recognize_hand_gesture(self.gesture_names[self.currentGesture_idx],  frame, self.draw_feedback)
                # only draw feedback when buffer is full
                if self.draw_feedback: 
                    self.draw_feedback = False
                self.prediction_buffer.append(prediction)
                prediction_count = self.prediction_buffer.count(self.gesture_names[self.currentGesture_idx])
                self.show_gesture_comment(status)
                if status == True and prediction_count >= 4 :
                    self.prediction_buffer.clear()
                    # continue to next gesture until the last gesture
                    if self.currentGesture_idx != len(self.gesture_names) - 1:
                        self.currentGesture_idx += 1
                        self.status_label.setText(f"Correct! Next gesture: {self.gesture_names[self.currentGesture_idx]}")
                        self.status_label.setStyleSheet("color: green;")
                    else:
                        self.finish_practice = True
                        self.clock.stop()
                        self.show_finish_practice()
                q_img = tool.frame2QImg(imgShow)

                # Check if buffer is full
                if len(self.prediction_buffer) == self.buffer_size//2:
                    self.draw_feedback = True
                if len(self.prediction_buffer) == self.buffer_size:
                    self.prediction_buffer.clear()  # Clear the buffer after processing

            else:
                if self.effect and  self.png_num <= self.effect_length:
                    q_img = self.play_effect(frame)
                    self.png_num += 1
                else:
                    q_img = tool.frame2QImg(frame)

            self.video_frame.setPixmap(QPixmap.fromImage(q_img))

    def show_gesture_comment(self, status):
        def correct_gesture(self):
            self.comment_label.setText("Correct Gesture!")
            self.comment_label.setStyleSheet(" color: green;")
        
        def wrong_gesture(self):
            self.comment_label.setText("Wrong Gesture!")
            self.comment_label.setStyleSheet(" color: red;")
            
        def show_hand_absence_alert(self):
            self.comment_label.setText("No hand detected!")
            self.comment_label.setStyleSheet(" color: red;")
            
        if status is None:
            show_hand_absence_alert(self)
        elif status == True:
            correct_gesture(self)
        else:
            wrong_gesture(self)
            
        
    def show_finish_practice(self):
        self.status_label.setText("You finish practice all selected gesture!")
        self.status_label.setStyleSheet(" color: green;")
    
    def play_effect(self, frame):
        frame = tool.add_gif2frame(self.effect, frame ,self.png_num)
        return frame
        
        
    def back_to_main(self):
        self.release_webcam()
        self.parent_widget.navigate_to_main_widget()
    
    def release_webcam(self):
        if self.cap.isOpened():
            self.cap.release()
            
    def reopen_webcam(self):
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
       

    

