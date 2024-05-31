import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock
from handGestureKnowledge import handGestureKnowledgeTaskWidget  # Adjust the import as needed
import tool
# Ensure QApplication is only created once
app = QApplication([])

@pytest.fixture
def mock_add_question_score_task1_callback():
    return Mock()

@pytest.fixture
def widget(mock_add_question_score_task1_callback, qtbot):
    gesture_name = "TestGesture"
    question = "What is this gesture?"
    options = ["Option 1", "Option 2", "Option 3"]
    answer = "Option 2"
    widget = handGestureKnowledgeTaskWidget(
        gesture_name,
        question,
        options,
        answer,
        mock_add_question_score_task1_callback,
        parent=None
    )
    qtbot.addWidget(widget)
    return widget

def test_initial_state(widget):
    assert widget.gesture_name == "TestGesture"
    assert widget.question == "What is this gesture?"
    assert widget.options == ["Option 1", "Option 2", "Option 3"]
    assert widget.answer == "Option 2"

    assert widget.question_label.text() == "Question: What is this gesture?"
    assert widget.result_label.text() == ""

    for i, btn in enumerate(widget.option_buttons):
        assert btn.text() == f"{['A.', 'B.', 'C.'][i]} {widget.options[i]}"

def test_option_selection(widget, mock_add_question_score_task1_callback, qtbot):
    # Select the correct option
    correct_option_button = widget.option_buttons[1]
    qtbot.mouseClick(correct_option_button, Qt.LeftButton)
    
    assert widget.result == True
    assert widget.result_label.text() == "Correct!"
     
    # reset the button state
    widget.result_label.setText("")
    for btn in widget.option_buttons:
            btn.setEnabled(True)
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

    # Select an incorrect option
    incorrect_option_button = widget.option_buttons[0]
    qtbot.mouseClick(incorrect_option_button, Qt.LeftButton)
    
    assert widget.result == False
    assert widget.result_label.text() == "Wrong! The correct option is Option 2."
    
