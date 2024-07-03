from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QGroupBox, QPushButton, QSizePolicy, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from gesture_constants import GESTURES

class handGesturePracticeWidget(QWidget):
    def __init__(self, start_practice_callback, parent=None):
        super().__init__(parent)
        
        self.start_practice_callback = start_practice_callback
        self.gesture_names = []
        self.selected_effect = None
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0) 

        # Gesture images layout
        gesture_layout = QHBoxLayout()
        gesture_layout.setSpacing(0)
        gesture_layout.setContentsMargins(0, 0, 0, 0)
        gestures = GESTURES
        
        for i, gesture_name in enumerate(gestures):
            img = f'images/handGesture/{gesture_name}.png'
            pixmap = QPixmap(img)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio) 
            gesture_icon = QLabel()
            gesture_icon.setPixmap(pixmap)
            gesture_icon.setAlignment(Qt.AlignCenter)
            gesture_icon.setFixedSize(100, 100)
            
            vbox = QVBoxLayout()
            vbox.setSpacing(0)  
            vbox.addWidget(gesture_icon)
            name_label = QLabel(f"{i+1}. {gesture_name}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFixedSize(100, 30)
            vbox.addWidget(name_label)
            
            container = QWidget()
            container.setLayout(vbox)
            
            gesture_layout.addWidget(container)

        layout.addLayout(gesture_layout) 

        # Instruction label
        instruction_label = QLabel("Please input the order of the hand gesture: (at least one):")
        instruction_label.setStyleSheet("font-size: 16px;border:none;")
        instruction_label.setFixedSize(800, 50)
        instruction_label.setContentsMargins(-1, -1, -1, 0)
        layout.addWidget(instruction_label, alignment=Qt.AlignLeft)

        # Text input for gesture order
        self.gesture_order_input = QLineEdit()
        self.gesture_order_input.setPlaceholderText('Please Input the number next to the hand gesture with space e.g."1 3 5 6 4"')
        self.gesture_order_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.gesture_order_input.setFixedSize(800, 30)
        self.gesture_order_input.setAlignment(Qt.AlignTop)
        layout.addWidget(self.gesture_order_input, alignment=Qt.AlignLeft)

        # Connect the textChanged signal to the next button
        self.gesture_order_input.textChanged.connect(self.update_button_state)

        # Desired effect label
        effect_label = QLabel("Please choose the desired effect after finishing the practice:")
        effect_label.setStyleSheet("font-size: 16px;border:none;")
        effect_label.setFixedSize(800, 50)
        layout.addWidget(effect_label, alignment=Qt.AlignLeft)

        # Radio buttons for desired effect
        self.effect_group = QGroupBox()
        self.effect_group.setStyleSheet("background-color: transparent; border: none;")
        
        # layout for radio buttons
        effect_layout = QVBoxLayout()
        effect_layout.setSpacing(0) 
        effect_layout.setContentsMargins(0, 0, 0, 0) 
        
        self.fire_effect = QRadioButton("Fire effect")
        self.thunder_effect = QRadioButton("Thunder effect")
        self.lighting_effect = QRadioButton("Lighting effect")
        
        self.fire_effect.toggled.connect(lambda: self.update_selected_effect("fire_effect"))
        self.thunder_effect.toggled.connect(lambda: self.update_selected_effect("thunder_effect"))
        self.lighting_effect.toggled.connect(lambda: self.update_selected_effect("lighting_effect"))
        
        # Style the radio buttons
        self.fire_effect.setFixedSize(200, 30)
        self.fire_effect.setStyleSheet("font-size: 16px; ")
        self.thunder_effect.setFixedSize(200, 30)
        self.thunder_effect.setStyleSheet("font-size: 16px;")
        self.lighting_effect.setFixedSize(200, 30)
        self.lighting_effect.setStyleSheet("font-size: 16px;")

        effect_layout.addWidget(self.fire_effect)
        effect_layout.addWidget(self.thunder_effect)
        effect_layout.addWidget(self.lighting_effect)

        self.effect_group.setLayout(effect_layout)
        layout.addWidget(self.effect_group, alignment=Qt.AlignTop)

        # Submit button (arrow button)
        self.next_btn = QPushButton("→")
        self.next_btn.setStyleSheet("""
            font-size: 24px;
            padding: 10px;
            border: 1px solid black;
            border-radius: 10px;
            background-color: white;
            color: black;
        """)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.start_practice)
        self.next_btn.setEnabled(False)  # only enable the button when there is input

        layout.addWidget(self.next_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def update_button_state(self):
        input_value = self.gesture_order_input.text().strip()
        self.next_btn.setEnabled(bool(input_value))

    def start_practice(self):
        input_value = self.gesture_order_input.text().strip()
        checked = self.check_input_value(input_value)
        if checked: 
            self.gesture_names = self.get_input_gesture_names(input_value)
            self.start_practice_callback(self.gesture_names, self.selected_effect)
        

    def get_input_gesture_names(self, input_gesture_order):
        gesture_names = []
        for i in input_gesture_order.split():
            gesture_names.append(GESTURES[int(i)-1])
        return gesture_names

    def update_selected_effect(self, effect_name):
        self.selected_effect = effect_name
        print("update_selected_effect", self.selected_effect)
    
    def check_input_value(self, input_value):
        if not input_value: 
            QMessageBox.warning(self, "Input Error", "Please input at least one number.")
            return False
        if len(input_value.split()) > 9:
            QMessageBox.warning(self, "Input Error", "Please input at most 9 number.")
            return False
        for num in input_value.split():
            try:
                if int(num) < 1 or int(num) > 9:
                    QMessageBox.warning(self, "Input Error", "Please input number between 1 to 9.")
                    return False
            except ValueError:
                    QMessageBox.warning(self, "Input Error", "Please input integer.")
                    return False
        return True
            
