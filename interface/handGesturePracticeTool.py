import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import os

# Add model path
abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../model'))
sys.path.insert(0, abs_path)
import utils
import mediapipe as mp
import numpy as np
import tensorflow as tf

class handGesturePracticeToolWidget(QWidget):
    def __init__(self, gesture_names, parent=None):
        super().__init__(parent)

        # Layout setup
        main_layout = QVBoxLayout()
        
        # Timer label
        self.time_label = QLabel("Time: 60s")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(self.time_label, alignment=Qt.AlignCenter)
        
        # Recognition widget
        self.recognition_widget = HandGestureRecognitionWidget("Recognition")
        main_layout.addWidget(self.recognition_widget, alignment=Qt.AlignCenter)

        # Gesture images layout
        self.gesture_layout = QHBoxLayout()
        self.gesture_layout.setSpacing(0)  # Set spacing to 0
        self.gesture_layout.setContentsMargins(0, 0, 0, 0)
        for gesture_name in gesture_names:
            img = f'images/handGesture/{gesture_name}.png'
            pixmap = QPixmap(img).scaled(100, 100, Qt.KeepAspectRatio)
            gesture_icon = QLabel()
            gesture_icon.setPixmap(pixmap)
            gesture_icon.setAlignment(Qt.AlignCenter)
            gesture_icon.setFixedSize(100, 100)
            self.gesture_layout.addWidget(gesture_icon)
        self.gesture_layout.addStretch(1)
        main_layout.addLayout(self.gesture_layout)

        self.setLayout(main_layout)

        # Start the timer
        self.start_timer(60)

    def start_timer(self, duration):
        self.time = QTime(0, duration, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
    def update_timer(self):
        self.time = self.time.addSecs(-1)
        self.time_label.setText(f"Time: {self.time.toString('mm:ss')}")
        if self.time.toString('mm:ss') == "00:00":
            self.timer.stop()
            # Perform any end-of-timer actions here

class HandGestureRecognitionWidget(QWidget):
    def __init__(self, gesture_name,  parent=None):
        super().__init__(parent)
        
        # Hand gesture recognition setup
        self.LENIENCY = 100
        self.target_size = (224, 224)
        self.cap = cv2.VideoCapture(0)
        mpHands = mp.solutions.hands
        self.hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.1, min_tracking_confidence=0.1)
        self.model = tf.keras.models.load_model("Model/color_fps4_hand_splited_dataset.h5")
        
        # Layout
        self.layout = QVBoxLayout(self)
        
        if not gesture_name:
            gesture_name = 'Testing'

        # Add webcam feed
        self.video_frame = QLabel(f"{gesture_name} Recognition Task")
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setFixedSize(768, 576)
        self.video_frame.setAlignment(Qt.AlignCenter)
        self.video_frame.setStyleSheet("font: 15px;")
        self.layout.addWidget(self.video_frame, alignment=Qt.AlignCenter)
        
        # Add start button
        self.startBtn = QPushButton("Start!")
        self.startBtn.setFixedSize(100, 50)
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.setStyleSheet("background-color:green; border: none; font: 15px; color: white;")
        self.startBtn.clicked.connect(lambda checked: self.toggleStart())
        self.layout.addWidget(self.startBtn, alignment=Qt.AlignCenter)
        
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
        self.timer.start(20)

        # Label for status and result
        self.status_label = QLabel("Hand Gesture Correct!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: green;")
        self.layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            q_img = self.recognize_hand_gesture(frame)
            self.video_frame.setPixmap(QPixmap.fromImage(q_img))
    
    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()

