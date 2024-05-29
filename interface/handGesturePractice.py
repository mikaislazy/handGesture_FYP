from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QGroupBox, QPushButton, QSizePolicy)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from tool import GESTURES

class handGesturePracticeWidget(QWidget):
    def __init__(self, start_practice_callback, parent=None):
        super().__init__(parent)
        
        self.start_practice_callback = start_practice_callback
        self.gesture_names = []
        self.selected_effect = None
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        main_layout.setSpacing(0)  # Set spacing to 0

        # Gesture images layout
        gesture_layout = QHBoxLayout()
        gesture_layout.setSpacing(0)  # Set spacing to 0
        gesture_layout.setContentsMargins(0, 0, 0, 0)
        gestures = GESTURES
        
        for i, gesture_name in enumerate(gestures):
            img = f'images/handGesture/{gesture_name}.png'
            pixmap = QPixmap(img)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)  # Scale the pixmap
            gesture_icon = QLabel()
            gesture_icon.setPixmap(pixmap)
            gesture_icon.setAlignment(Qt.AlignCenter)
            gesture_icon.setFixedSize(100, 100)
            
            vbox = QVBoxLayout()
            vbox.setSpacing(0)  # Set spacing to 0
            vbox.addWidget(gesture_icon)
            name_label = QLabel(f"{i+1}. {gesture_name}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFixedSize(100, 30)
            vbox.addWidget(name_label)
            
            container = QWidget()
            container.setLayout(vbox)
            
            gesture_layout.addWidget(container)

        main_layout.addLayout(gesture_layout)  # Center the gesture layout

        # Instruction label
        instruction_label = QLabel("Please input the order of the hand gesture: (at least one):")
        instruction_label.setStyleSheet("font-size: 16px;border:none;")
        instruction_label.setFixedSize(800, 50)
        instruction_label.setContentsMargins(-1, -1, -1, 0)
        main_layout.addWidget(instruction_label, alignment=Qt.AlignLeft)

        # Text input for gesture order
        self.gesture_order_input = QLineEdit()
        self.gesture_order_input.setPlaceholderText('Please Input the number next to the hand gesture with space e.g."1 3 5 6 4"')
        self.gesture_order_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.gesture_order_input.setFixedSize(800, 30)
        self.gesture_order_input.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.gesture_order_input, alignment=Qt.AlignLeft)

        # Connect the textChanged signal to the method that enables/disables the button
        self.gesture_order_input.textChanged.connect(self.update_button_state)

        # Desired effect label
        effect_label = QLabel("Please choose the desired effect after finishing the practice:")
        effect_label.setStyleSheet("font-size: 16px;border:none;")
        effect_label.setFixedSize(800, 50)
        main_layout.addWidget(effect_label, alignment=Qt.AlignLeft)

        # Radio buttons for desired effect
        self.effect_group = QGroupBox()
        self.effect_group.setStyleSheet("background-color: transparent; border: none;")
        
        # layout for radio buttons
        effect_layout = QVBoxLayout()
        effect_layout.setSpacing(0)  # Set spacing to 0
        effect_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        
        self.fire_effect = QRadioButton("Fire effect")
        self.thunder_effect = QRadioButton("Thunder effect")
        self.lighting_effect = QRadioButton("Lighting effect")
        
        self.fire_effect.toggled.connect(lambda: self.update_selected_effect("fire_effect"))
        self.thunder_effect.toggled.connect(lambda: self.update_selected_effect("thunder_effect"))
        self.lighting_effect.toggled.connect(lambda: self.update_selected_effect("lighting_effect"))
        # style the radio buttons
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
        main_layout.addWidget(self.effect_group, alignment=Qt.AlignTop)

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
        self.next_btn.setEnabled(False)  # Initially disable the button

        main_layout.addWidget(self.next_btn, alignment=Qt.AlignRight)

        self.setLayout(main_layout)

    def update_button_state(self):
        input_value = self.gesture_order_input.text().strip()
        self.next_btn.setEnabled(bool(input_value))

    def start_practice(self):
        input_value = self.gesture_order_input.text().strip()
        if input_value:  # Check if input_value is not empty
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
