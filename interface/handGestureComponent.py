from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QStackedWidget, QMainWindow, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from handGestureTaskSelection import handGestureTaskSelectionWidget
from tool import GESTURES
from handGestureKnowledge import handGestureKnowledgeTaskWidget

class handGestureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(1000)
        self.setStyleSheet("""
            QPushButton {
                border: none;  /* No border for buttons */
                background-color: transparent;  /* Transparent background to show icon only */
            }
            QPushButton:pressed {
                background-color: #DDDDDD;  /* Slight grey background when pressed */
            }
        """)

        self.original_size = self.size()  # Original size of the window

        self.layout = QHBoxLayout(self)
        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Gesture layout
        self.gesture_widget = QWidget()
        gesture_layout = QGridLayout()
        self.gesture_widget.setLayout(gesture_layout)

        # Stacked Layout
        self.stacked_widget = None  # Initially, there's no stacked widget

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
            btn.clicked.connect(lambda checked, n=name: self.openTaskSelection(n))
            row, col = divmod(i, 3)
            gesture_layout.addWidget(btn, row, col)

        # Practice button
        btn_practice = QPushButton()
        btn_practice.setIcon(QIcon('images/otherBtn/practiceBtn.png'))
        btn_practice.setIconSize(QSize(300, 300))
        btn_practice.setFixedSize(300, 300)
        btn_practice.setCursor(Qt.PointingHandCursor)
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

    def openTaskSelection(self, gesture_name):
        self.gesture_widget.hide()
        self.btn_practice_widget.hide()

        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)

        self.taskSelection = handGestureTaskSelectionWidget(
            gesture_name, 
            self.start_gesture_knowledge_task, 
            parent=self
        )
        self.stacked_widget.addWidget(self.taskSelection)
        self.stacked_widget.setCurrentWidget(self.taskSelection)

    def start_gesture_knowledge_task(self, gesture_name, questions, options, answers):
        self.stacked_questions = QStackedWidget(self)
        # self.stacked_questions.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        for q, opt, ans in zip(questions, options, answers):
            question_widget = handGestureKnowledgeTaskWidget(q, opt, ans, self)
            self.stacked_questions.addWidget(question_widget)

        self.stacked_widget.addWidget(self.stacked_questions)
        self.stacked_widget.setCurrentWidget(self.stacked_questions)
        self.navigate_to_question(self.stacked_questions.widget(0))

    def navigate_to_main_widget(self):
        self.resize(self.original_size )
        self.gesture_widget.show()
        self.btn_practice_widget.show()

        if self.stacked_widget is not None:
            self.layout.removeWidget(self.stacked_widget)
            self.stacked_widget.deleteLater()
            self.stacked_widget = None

        # Set the geometry of the main window directly
        # main_window = self.find_main_window()
        # if main_window:
        #     print("main window is found")
        #     main_window.resize_main_window()

        # self.layout.setStretch(0, 1)
        # self.layout.setStretch(1, 0)
        # self.layout.setStretch(2, 0)

    def navigate_to_question(self, question_widget):
        self.stacked_widget.setCurrentWidget(question_widget)

    def find_main_window(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None
