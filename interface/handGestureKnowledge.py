import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
import json 

class handGestureKnowledgeTaskWidget(QWidget):
    def __init__(self,gesture_name, parent=None):
        super().__init__(parent)
        
        # Load questions from JSON file
        with open('other/question.json', 'r') as f:
            question_bank = json.load(f)
            q_opt = question_bank[gesture_name]['questions'][0] # take the first as testing
            questions = q_opt['question']
            options = q_opt['options']
            
        #load answer from JSON file
        with open('other/answer.json', 'r') as f:
            answers = json.load(f)
            q_a = answers[gesture_name]["answers"][0]
            answer = q_a['correct_option']
        
        # layout 
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Question label
        self.question_label = QLabel(f"Question: {questions}")
        self.question_label.setFixedSize(800, 80)
        self.question_label.setWordWrap(True) 
        self.question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            border: 1px solid black;
            border-radius: 10px;
            color: black;
            background-color: white;
            padding: 10px;
        """)

        layout.addWidget(self.question_label, alignment=Qt.AlignCenter)
        # layout.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Options buttons
        self.optionGroup = QButtonGroup()
        self.option_buttons = []
        opt_order = ["A.", "B.", "C."]
        
        for order, option_text in zip(opt_order, options):
            button = QPushButton(f"{order} {option_text}")
            button.setFixedSize(700, 50)
            button.setStyleSheet("""
                font-size: 16px;
                padding: 10px;
                border: 1px solid black;
                border-radius: 5px;
                background-color: white;
                color: black;
                text-align: left;
                margin: 0;
            """)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(self.on_option_click)
            self.option_buttons.append(button)
            self.optionGroup.addButton(button)
            layout.addWidget(button, alignment=Qt.AlignCenter)
            
        # add question and option to the layout
        self.setLayout(layout)

    def on_option_click(self):
        sender = self.sender()
        print(f'Button clicked: {sender.text()}')
