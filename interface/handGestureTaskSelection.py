import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

class TaskSelectionWidget(QWidget):
    def __init__(self, gesture_name, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        print(f"{gesture_name}'s Task is open for selection")

        # Gesture layout
        # Create two buttons
        image_path = f'images/handGesture/{gesture_name}.png'
        for i in range(2):
            gesture_layout = QVBoxLayout()
            gesture_layout.setContentsMargins(0, 0, 0, 0) 
            # gesture_layout.setSpacing(0)
            
            # Create a button and set its text and icon
            btn = QPushButton(gesture_name)
            btn.setContentsMargins(0, 0, 0, 0)
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(150, 150))
            btn.setFixedSize(300, 400)  # Set the size of the buttons
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background-color:white; border: none;")
            
            # Add the appropriate task label
            task_label = QLabel()
            # task_label.setContentsMargins(0, 0, 0, 0)
            task_label.setFixedSize(200, 50)
            task_label.setWordWrap(True) 
            task_label.setStyleSheet("font-size: 20px;")  
            if i == 0:
                task_label.setText('Hand Gesture Knowledge Task')
            else:
                task_label.setText('Hand Gesture Recognition Task')

            # Add widgets to the layout
            gesture_layout.addWidget(task_label)
            gesture_layout.addWidget(btn)
            gesture_layout.addStretch(1) 
            layout.addLayout(gesture_layout)
