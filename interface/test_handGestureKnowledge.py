import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock
from handGestureKnowledge import handGestureKnowledgeTaskWidget  # Adjust the import as needed
import tool


@pytest.fixture
def mock_add_question_score_task1_callback():
    return Mock()

@pytest.fixture
def app(mock_add_question_score_task1_callback, qtbot):
    gesture_name = "TestGesture"
    question = "What is this gesture?"
    options = ["Option 1", "Option 2", "Option 3"]
    answer = "Option 2"
    test_handGestureKnowledgeTaskWidget = handGestureKnowledgeTaskWidget(
        gesture_name,
        question,
        options,
        answer,
        mock_add_question_score_task1_callback,
        parent=None
    )
    qtbot.addWidget(test_handGestureKnowledgeTaskWidget)
    return test_handGestureKnowledgeTaskWidget

def test_initial_state(app):
    assert app.gesture_name == "TestGesture"
    assert app.question == "What is this gesture?"
    assert app.options == ["Option 1", "Option 2", "Option 3"]
    assert app.answer == "Option 2"

    assert app.question_label.text() == "Question: What is this gesture?"
    assert app.result_label.text() == ""

    for i, btn in enumerate(app.option_buttons):
        assert btn.text() == f"{['A.', 'B.', 'C.'][i]} {app.options[i]}"

def test_option_selection(app, mock_add_question_score_task1_callback, qtbot):
    # Select the correct option
    correct_option_button = app.option_buttons[1]
    qtbot.mouseClick(correct_option_button, Qt.LeftButton)
    
    assert app.result == True
    assert app.result_label.text() == "Correct!"
     
    # reset the button state
    app.result_label.setText("")
    for btn in app.option_buttons:
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
    incorrect_option_button = app.option_buttons[0]
    qtbot.mouseClick(incorrect_option_button, Qt.LeftButton)
    
    assert app.result == False
    assert app.result_label.text() == "Wrong! The correct option is Option 2."
    
