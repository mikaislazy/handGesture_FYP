from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from handGestureKnowledge import handGestureKnowledgeTaskWidget
from tool import load_question, load_answer

class handGestureTaskSelectionWidget(QWidget):
    def __init__(self, gesture_name, start_knowledge_task_callback, parent=None):
        super().__init__(parent)
        print("selecting hand gesture task...")
        self.layout = QHBoxLayout(self)
        self.gesture_name = gesture_name
        self.start_knowledge_task_callback = start_knowledge_task_callback

        for i in range(2):
            gesture_layout = QVBoxLayout()
            gesture_layout.setContentsMargins(0, 0, 0, 0)
            
            btn = QPushButton(gesture_name)
            btn.setContentsMargins(0, 0, 0, 0)
            btn.setIcon(QIcon(f'images/handGesture/{gesture_name}.png'))
            btn.setIconSize(QSize(150, 150))
            btn.setFixedSize(300, 400)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background-color:white; border: none;")
            
            task_label = QLabel()
            task_label.setFixedSize(200, 50)
            task_label.setWordWrap(True)
            task_label.setStyleSheet("font-size: 20px;")
            if i == 0:
                task_label.setText('Hand Gesture Knowledge Task')
                btn.clicked.connect(self.start_gesture_knowledge_task)
            else:
                task_label.setText('Hand Gesture Recognition Task')
                # btn.clicked.connect(self.start_gesture_recognition_task)

            gesture_layout.addWidget(task_label)
            gesture_layout.addWidget(btn)
            gesture_layout.addStretch(1)
            self.layout.addLayout(gesture_layout)

    def start_gesture_knowledge_task(self):
        gesture_name = self.gesture_name
        questions, options = load_question(gesture_name, 'other/question.json')
        answers = load_answer(gesture_name, 'other/answer.json')
        self.start_knowledge_task_callback(gesture_name, questions, options, answers)
