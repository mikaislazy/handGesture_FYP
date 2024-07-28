from PyQt5.QtWidgets import QWidget,  QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QMainWindow, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from handGestureTaskSelection import handGestureTaskSelectionWidget
from gesture_constants import GESTURES
from handGestureKnowledge import handGestureKnowledgeTaskWidget
from handGestureRecognition import  handGestureRecognitionWidget
from handGesturePractice import handGesturePracticeWidget
from handGesturePracticeTool import handGesturePracticeToolWidget
from  UserData import db_utils 

class handGestureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(1200)
        self.setStyleSheet("""
            QPushButton {
                border: none;  
                background-color: transparent; 
            }
            QPushButton:pressed {
                background-color: #DDDDDD; 
            }
        """)


        self.layout = QHBoxLayout(self)
        # Gesture layout
        self.gesture_widget = QWidget()
        gesture_layout = QGridLayout()
        self.gesture_widget.setLayout(gesture_layout)

        # Stacked Layout
        self.stacked_widget = QStackedWidget(self) 

        for i, name in enumerate(GESTURES):
            image_path = f'images/handGestureBtn/{name}Btn.png'
            btn = QPushButton()
            btn.setIcon(QIcon(image_path))
            btn.setIconSize(QSize(200, 200))
            btn.setFixedSize(200, 200)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 0;
                    background-color: transparent;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.open_task_selection(n))
            row, col = divmod(i, 3)
            gesture_layout.addWidget(btn, row, col)

        # Practice button
        btn_practice = QPushButton()
        btn_practice.setIcon(QIcon('images/otherBtn/practiceBtn.png'))
        btn_practice.setIconSize(QSize(300, 300))
        btn_practice.setFixedSize(300, 300)
        btn_practice.setCursor(Qt.PointingHandCursor)
        btn_practice.clicked.connect(self.open_practice_tool)
        btn_practice.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0;
                background-color: transparent;
            }
        """)

        self.btn_practice_widget = QWidget()
        btn_practice_layout = QGridLayout()
        btn_practice_layout.addWidget(btn_practice)
        self.btn_practice_widget.setLayout(btn_practice_layout)
        
        # Layout add widget
        self.layout.addWidget(self.gesture_widget)
        self.layout.addWidget(self.btn_practice_widget)

    def open_task_selection(self, gesture_name):
        self.gesture_widget.hide()
        self.btn_practice_widget.hide()
        
        self.layout.addWidget(self.stacked_widget)

        self.task_selection_widget = handGestureTaskSelectionWidget(
            gesture_name, 
            self.start_gesture_knowledge_task,
            self.start_gesture_recognition_task,
            parent=self
        )
        self.stacked_widget.addWidget(self.task_selection_widget)
        self.stacked_widget.setCurrentWidget(self.task_selection_widget)
    
    def open_practice_tool(self):
        self.gesture_widget.hide()
        self.btn_practice_widget.hide()
        
        self.layout.addWidget(self.stacked_widget)
        
        self.practice_widget = handGesturePracticeWidget(self.start_practice, self)
        self.stacked_widget.addWidget(self.practice_widget)
        self.stacked_widget.setCurrentWidget(self.practice_widget)
        
    def start_gesture_knowledge_task(self, gesture_name, questions, options, answers):
        self.trial_score = 0
        self.stacked_questions = QStackedWidget(self)
        
        for q, opt, ans in zip(questions, options, answers):
            question_widget = handGestureKnowledgeTaskWidget(gesture_name,q, opt, ans, self.add_question_score_task1, self)
            self.stacked_questions.addWidget(question_widget)

        self.stacked_widget.addWidget(self.stacked_questions)
        self.stacked_widget.setCurrentWidget(self.stacked_questions)
        self.navigate_to_question(self.stacked_questions.widget(0))

    def start_gesture_recognition_task(self, gesture_name, method):
        self.recognition_widget = handGestureRecognitionWidget(gesture_name,self.insert_record_task2 , method, self)
        self.stacked_widget.addWidget(self.recognition_widget)
        self.stacked_widget.setCurrentWidget(self.recognition_widget)
    
    def start_practice(self, gesture_names, effect_name):
        self.practiceTool_widget = handGesturePracticeToolWidget(gesture_names, effect_name,self)
        self.stacked_widget.addWidget(self.practiceTool_widget)
        self.stacked_widget.setCurrentWidget(self.practiceTool_widget)

    def navigate_to_main_widget(self):
        self.gesture_widget.show()
        self.btn_practice_widget.show()

        self.layout.removeWidget(self.stacked_widget)
        self.stacked_widget = QStackedWidget(self) 

    def navigate_to_question(self, question_widget):
        self.stacked_widget.setCurrentWidget(question_widget)

    def find_main_window(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None
    
    def add_question_score_task1(self, gesture_name, score, is_last_question):
        self.trial_score += score
        if is_last_question:
            db_utils.insert_record_task1(gesture_name, self.trial_score)
    
    def insert_record_task2(self, gesture_name, status, duration):
        db_utils.insert_record_task2(gesture_name, status, duration)
        
            
            
        
        
