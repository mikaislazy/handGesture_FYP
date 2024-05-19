import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from handGestureTaskSelection import TaskSelectionWidget

class HandGestureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            # QWidget {
            #     background-color: #FFFFFF;  /* Set the main background to white */
            # }
            QPushButton {
                border: none;  /* No border for buttons */
                background-color: transparent;  /* Transparent background to show icon only */
            }
            QPushButton:pressed {
                background-color: #DDDDDD;  /* Slight grey background when pressed */
            }
        """)
        
        layout = QHBoxLayout(self)
        
        # Gesture layout
        
        # add Gesture button to the private variables and save in layout
        self.gesture_widget = QWidget()
        gesture_layout = QGridLayout()
        self.gesture_widget.setLayout(gesture_layout)
        layout.addWidget(self.gesture_widget)
        
        # Stacked Layout
        self.stacked_widget= QStackedWidget(self)
        layout.addWidget(self.stacked_widget) 
        
        # Gestures
        gestures = [
            'HuoYanYin',
            'ChanDingYin',
            'MiTuoDingYin',
            'Retsu',
            'Rin',
            'Zai',
            'Zen',
            'ZhiJiXiangYin',
            'TaiJiYin'
        ]

        for i, name in enumerate(gestures):
            image_path = f'images/handGestureBtn/{name}Btn.png'
            btn = QPushButton()
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(200, 200))  # Ensure the icon size fits the button
            btn.setFixedSize(200, 200)  # Set the size of the buttons
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 0;
                    background-color: transparent;
                }
            """)  # Remove border and padding, set background to transparent
            btn.clicked.connect(lambda checked, n=name: self.openTaskSelection(n))
            row, col = divmod(i, 3)
            gesture_layout.addWidget(btn, row, col)

        # Practice button
        btn_practice = QPushButton()
        btn_practice.setIcon(QIcon('images/otherBtn/practiceBtn.png'))
        btn_practice.setIconSize(QSize(300, 300))  # Ensure the icon size fits the button
        btn_practice.setFixedSize(300, 300)
        btn_practice.setCursor(Qt.PointingHandCursor)
        btn_practice.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0;
                background-color: transparent;
            }
        """)  # Remove border and padding, set background to transparent
        
        # add Practice button to the private variables and save in layout
        self.btn_practice_widget = QWidget()
        btn_practice_layout = QGridLayout()
        btn_practice_layout.addWidget(btn_practice)
        self.btn_practice_widget.setLayout(btn_practice_layout)
        layout.addWidget(self.btn_practice_widget)
        # layout.addWidget(btn_practice)
    
    def openTaskSelection(self, gesture_name):
        # Placeholder function to handle gesture button clicks
        print(f'Gesture {gesture_name} clicked!')
        # hide the handGestureSelection widget
        self.gesture_widget.hide()
        self.btn_practice_widget.hide()
        self.stacked_widget.setCurrentIndex(0)
        # Add the gesture layout to the QStackedWidget
        self.taskSelection = TaskSelectionWidget(gesture_name)
        self.stacked_widget.addWidget(self.taskSelection)
        self.stacked_widget.setCurrentWidget(self.taskSelection)

