import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QHBoxLayout
from PyQt5.QtCore import Qt

class handGestureKnowledgeTaskWidget(QWidget):
    def __init__(self, question, options, answer, parent=None):
        super().__init__(parent)
        print(f"Completed hand gesture question: {question}")
        self.question = question
        self.options = options
        self.answer = answer
        self.parent_widget = parent
        
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
        self.optionGroup = QButtonGroup()
        self.optionGroup.setExclusive(True)
        self.option_buttons = []
        opt_order = ["A.", "B.", "C."]
        
        for order, option_text in zip(opt_order, options):
            btn = QPushButton(f"{order} {option_text}")
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
            btn.clicked.connect(lambda checked, option_text=option_text: self.on_option_click(option_text))
            self.option_buttons.append(btn)
            self.optionGroup.addButton(btn)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)    
        # Set the layout only once
        self.setLayout(layout)

    def on_option_click(self, selected_option):
        print(f'Option clicked: {selected_option}')
        print(f"Correct answer: {self.answer}")
        parent = self.parentWidget().parentWidget()
        if selected_option.lower() == self.answer.lower():
            self.result_label.setText("Correct!")
            self.result_label.setStyleSheet("color: green;")
            self.navigate_to_next_question()
        else:
            self.parent_widget.navigate_to_main_widget()

    def navigate_to_next_question(self):
        parent = self.parent_widget
        current_index = parent.stacked_questions.currentIndex()
        if current_index < parent.stacked_questions.count() - 1:
            parent.stacked_questions.setCurrentIndex(current_index + 1)
        else:
            parent.navigate_to_main_widget()
