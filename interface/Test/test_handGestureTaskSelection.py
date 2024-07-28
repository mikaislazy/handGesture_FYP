import pytest
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton
from handGestureTaskSelection import handGestureTaskSelectionWidget
from unittest.mock import Mock

# Fixture to create a mock function of start_knowledge_task_callback
@pytest.fixture
def mock_start_knowledge_task_callback():
    return  Mock()

# Fixture to create a mock function of start_recognition_task_callback
@pytest.fixture
def mock_start_recognition_task_callback():
    return Mock()

# Fixture to create a temporary widget for testing
@pytest.fixture
def app(mock_start_knowledge_task_callback, mock_start_recognition_task_callback, qtbot):
    test_handGestureSelectionTask = handGestureTaskSelectionWidget('ChanDingYin', mock_start_knowledge_task_callback, mock_start_recognition_task_callback, None)
    qtbot.addWidget(test_handGestureSelectionTask)
    return test_handGestureSelectionTask

# Test the initial state of the widget
def test_initial_state(app, qtbot):
    widget = app.layout

    for i, layout in enumerate(widget.children()):
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


