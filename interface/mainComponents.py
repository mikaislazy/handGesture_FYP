import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from handGestureComponent import handGestureWidget 
from handGestureRecognition import handGestureRecognitionWidget
from handGestureKnowledge import handGestureKnowledgeTaskWidget
from handGesturePractice import handGesturePracticeWidget
from handGesturePracticeTool import handGesturePracticeToolWidget
from handGestureTaskSelection import handGestureTaskSelectionWidget

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('EdTech Application for learning Taoism and Buddhism gestures')
        self.setGeometry(100, 100, 1200, 800)  # Set the size of the main window

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QHBoxLayout(main_widget)
        
        # Sidebar layout
        sidebar_widget = QWidget()
        sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;  /* Light grey background */
                border-right: 1px solid #dcdcdc;  /* Light grey right border */
            }
            QPushButton {
                border: none;  /* No border for buttons */
                background-color: #f0f0f0;  /* Light grey background */
                padding: 10px;
                text-align: left;
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;  /* Slightly darker grey when pressed */
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        main_layout.addWidget(sidebar_widget)
        
        # Dashboard button
        btn_dashboard = QPushButton('Dashboard')
        sidebar_layout.addWidget(btn_dashboard)
        
        # User button
        btn_user = QPushButton('User')
        sidebar_layout.addWidget(btn_user)
        
        # Setting button
        btn_setting = QPushButton('Setting')
        sidebar_layout.addWidget(btn_setting)
        
        # Spacer
        sidebar_layout.addStretch()

        # Central widget layout
        self.central_widget = QStackedWidget()
        main_layout.addWidget(self.central_widget)
        
        # Create and add the hand gesture learning widget
        self.hand_gesture_widget = handGestureWidget(self)
        self.central_widget.addWidget(self.hand_gesture_widget)
        self.central_widget.setCurrentWidget(self.hand_gesture_widget)
        
        # Set the testing widget to hand gesture learning
        # self.testingWidget = handGestureWidget(self)
        # self.central_widget.addWidget(self.testingWidget)

    def resize_main_window(self):
        print('try to resize back the orignal window')
        self.setGeometry(100, 100, 1200, 800)
