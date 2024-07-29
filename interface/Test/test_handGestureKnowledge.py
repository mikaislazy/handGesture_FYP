import pytest
from PyQt5.QtCore import Qt
from unittest.mock import Mock
from handGestureKnowledge import handGestureKnowledgeTaskWidget 
import tool 

# Fixture to create a mock function of add_question_score_task1_callback
@pytest.fixture
def mock_add_question_score_task1_callback():
    return Mock()

gesture_name = "ChanDingYin"
gesture_questions, gesture_options = tool.load_question(gesture_name, 'Widgets/other/question.json')
question = gesture_questions[0]
options = gesture_options[0]
gesture_answers = tool.load_answer(gesture_name, 'Widgets/other/answer.json')
answer = gesture_answers[0]
answer_index = options.index(answer)
# Fixture to create a temporary widget for testing
@pytest.fixture
def app(mock_add_question_score_task1_callback, qtbot):
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

# Test the initial state of the widget
def test_initial_state(app):
    assert app.gesture_name == gesture_name
    assert app.question == question
    assert app.options == options
    assert app.answer == answer

    assert app.question_label.text() == f"Question: {question}"
    assert app.result_label.text() == ""

    for i, btn in enumerate(app.opt_buttons):
        assert btn.text() == f"{['A.', 'B.', 'C.'][i]} {app.options[i]}"

# Test the option selection
def test_option_selection(app, mock_add_question_score_task1_callback, qtbot):
    # Select the correct option
    correct_option_button = app.opt_buttons[answer_index]
    qtbot.mouseClick(correct_option_button, Qt.LeftButton)
    
    assert app.result == True
    assert app.result_label.text() == "Correct!"
     
    # reset the button state
    app.result_label.setText("")
    for btn in app.opt_buttons:
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
    incorrect_option_button = app.opt_buttons[2-answer_index]
    qtbot.mouseClick(incorrect_option_button, Qt.LeftButton)
    
    assert app.result == False
    assert app.result_label.text() == f"Wrong! The correct option is {answer}."
    
