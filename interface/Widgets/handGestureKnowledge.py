import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import Qt

class handGestureKnowledgeTaskWidget(QWidget):
    def __init__(self, gesture_name, question, options, answer,add_question_score_task1_callback, parent=None):
        super().__init__(parent)
        self.gesture_name = gesture_name
        self.question = question
        self.options = options
        self.answer = answer
        self.add_question_score_task1_callback = add_question_score_task1_callback
        self.parent_widget = parent
        
        self.result = None
        
        # layout 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Question label
        self.question_label = QLabel(f"Question: {question}")
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
        
        # Options buttons
        self.opt_group = QButtonGroup()
        self.opt_group.setExclusive(True)
        self.opt_buttons = []
        opt_order = ["A.", "B.", "C."]
        
        for order, opt_text in zip(opt_order, options):
            btn = QPushButton(f"{order} {opt_text}")
            btn.setFixedSize(700, 50)
            btn.setStyleSheet("""
                font-size: 16px;
                padding: 10px;
                border: 1px solid black;
                border-radius: 5px;
                background-color: white;
                color: black;
                text-align: left;
                margin: 0;
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, opt_text=opt_text: self.on_option_click(opt_text))
            self.opt_buttons.append(btn)
            self.opt_group.addButton(btn)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)    
        
        # Next Button 
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedSize(150, 50)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet("background-color: #3ba6ff; border: none; font: 15px; color: white;")
        self.next_btn.clicked.connect(self.on_next_btn_clicked)
        layout.addWidget(self.next_btn, alignment=Qt.AlignRight)
        
        # Next button hide before the option is selected
        self.next_btn.hide()
        
        self.setLayout(layout)
        
    def on_next_btn_clicked(self):
        self.navigate_to_next_question()
        
    def on_option_click(self, selected_option):
        print(f'Option clicked: {selected_option}')
        print(f"Correct answer: {self.answer}")
        self.next_btn.show()
        if selected_option.lower() == self.answer.lower():
            self.result = True
            self.result_label.setText("Correct!")
            self.result_label.setStyleSheet("color: green; font:15px;")
            
        else:
            self.result = False
            self.result_label.setText(f"Wrong! The correct option is {self.answer}.")
            self.result_label.setStyleSheet("color: red;  font:15px;")
            
        if self.is_last_question():
            self.next_btn.setText("Back to Main Page")
            
        for btn in self.opt_buttons:
            btn.setEnabled(False)
            btn.setStyleSheet("""
                font-size: 16px;
                padding: 10px;
                border: 1px solid black;
                border-radius: 5px;
                background-color: grey;
                color: black;
                text-align: left;
                margin: 0;
            """)
        
        # add score
        self.add_question_score_task1_callback( self.gesture_name,self.result, self.is_last_question())
        

    def navigate_to_next_question(self):
        parent = self.parent_widget
        current_index = parent.stacked_questions.currentIndex()
        if not self.is_last_question():
            parent.stacked_questions.setCurrentIndex(current_index + 1)
        else:
            parent.navigate_to_main_widget()
    
    def is_last_question(self):
        parent = self.parent_widget
        if parent:
            current_index = parent.stacked_questions.currentIndex()
            if current_index == parent.stacked_questions.count() - 1:
                return True
        return False