import pytest
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from handGestureTaskSelection import handGestureTaskSelectionWidget
from handGestureComponent import handGestureWidget
from mainComponents import mainWindow
from unittest.mock import Mock



def mock_start_knowledge_task_callback():
    return 


def mock_start_recognition_task_callback():
    return 
# app_instance = QApplication([])
@pytest.fixture
def app(qtbot):
    print("Creating widget...")
    test_handGestureSelectionTask = handGestureTaskSelectionWidget('ChanDingYin', mock_start_knowledge_task_callback, mock_start_recognition_task_callback, None)
    print("Widget created:", test_handGestureSelectionTask)
    qtbot.addWidget(test_handGestureSelectionTask)
    return test_handGestureSelectionTask


def test_initial_state(app, qtbot):
    widget = app.layout
    # print(widget.children())

    for i, layout in enumerate(widget.children()):
        # print("test:", layout.itemAt(0).widget())
        task_label = layout.itemAt(0).widget()
        btn = layout.itemAt(1).widget()

        assert isinstance(task_label, QLabel)
        assert isinstance(btn, QPushButton)
        
        if i == 0:
            assert task_label.text() == 'Hand Gesture Knowledge Task'
            assert btn.text() == "ChanDingYin"
        else:
            assert task_label.text() == 'Hand Gesture Recognition Task'
            assert btn.text() == "ChanDingYin"


