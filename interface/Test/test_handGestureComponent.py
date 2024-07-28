from handGesturePracticeTool import handGesturePracticeToolWidget
from handGestureRecognition import handGestureRecognitionWidget
from handGestureTaskSelection import handGestureTaskSelectionWidget
from handGesturePractice import handGesturePracticeWidget
from mainComponents import mainWindow
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


# Ensure PyQt application is initialized once for the test session
@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

# Fixture to create the main window
@pytest.fixture
def main_window(app, qtbot):
    window = mainWindow()
    window.setAttribute(Qt.WA_DontShowOnScreen, True) # dont show the GUI on screen
    qtbot.addWidget(window)
    window.show()
    yield window
    window.close()

# Fixture to create the hand gesture widget within the main window
@pytest.fixture
def widget(main_window):
    widget = main_window.hand_gesture_widget
    return widget

# Test the initial state of the widget
def test_initial_state(widget):
    assert widget.isVisible()
    assert widget.gesture_widget.isVisible()
    assert widget.btn_practice_widget.isVisible()
    assert widget.stacked_widget.count() == 0

# Test opening the task selection
def test_open_task_selection(widget, qtbot):
    gesture_name = "TestGesture"
    qtbot.mouseClick(widget.gesture_widget.layout().itemAt(0).widget(), Qt.LeftButton)
    widget.open_task_selection(gesture_name)

    assert not widget.gesture_widget.isVisible()
    assert not widget.btn_practice_widget.isVisible()
    assert widget.stacked_widget.isVisible()
    assert isinstance(widget.stacked_widget.currentWidget(), handGestureTaskSelectionWidget)

# Test opening the practice tool
def test_open_practice_tool(widget, qtbot):
    qtbot.mouseClick(widget.btn_practice_widget.layout().itemAt(0).widget(), Qt.LeftButton)
    widget.open_practice_tool()

    assert not widget.gesture_widget.isVisible()
    assert not widget.btn_practice_widget.isVisible()
    assert widget.stacked_widget.isVisible()
    assert isinstance(widget.stacked_widget.currentWidget(), handGesturePracticeWidget)

# Test navigating back to the main widget
def test_navigate_to_main_widget(widget, qtbot):
    gesture_name = "TestGesture"
    qtbot.mouseClick(widget.gesture_widget.layout().itemAt(0).widget(), Qt.LeftButton)
    widget.open_task_selection(gesture_name)

    widget.navigate_to_main_widget()
    assert widget.gesture_widget.isVisible()
    assert widget.btn_practice_widget.isVisible()
    assert widget.stacked_widget.count() == 0

# Test starting the gesture recognition task
def test_start_gesture_recognition_task(widget):
    gesture_name = "TestGesture"
    widget.start_gesture_recognition_task(gesture_name, "Method of TestGesture")

    assert isinstance(widget.stacked_widget.currentWidget(), handGestureRecognitionWidget)

# Test starting the practice tool
def test_start_practice(widget):
    gesture_names = ["TestGesture1", "TestGesture2"]
    effect_name = "fire_effect"
    widget.start_practice(gesture_names, effect_name)

    assert isinstance(widget.stacked_widget.currentWidget(), handGesturePracticeToolWidget)

# Test adding a question score
def test_add_question_score_task1(widget):
    widget.trial_score = 0
    gesture_name = "TestGesture"
    score = 4
    is_last_question = True

    widget.add_question_score_task1(gesture_name, score, is_last_question)

    assert widget.trial_score == score

# Test inserting a record for task 2
def test_insert_record_task2(widget):
    gesture_name = "TestGesture"
    status = True
    duration = 50

    widget.insert_record_task2(gesture_name, status, duration)
