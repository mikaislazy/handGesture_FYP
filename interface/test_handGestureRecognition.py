import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
from handGestureRecognition import handGestureRecognitionWidget
from unittest.mock import Mock

@pytest.fixture
def mock_insert_record_task2_callback():
    return Mock()

@pytest.fixture
def app(mock_insert_record_task2_callback, qtbot):
    test_handGestureRecognitionWidget = handGestureRecognitionWidget('TestGesture', mock_insert_record_task2_callback)
    qtbot.addWidget(test_handGestureRecognitionWidget)
    return test_handGestureRecognitionWidget

def test_initial_state(app):
    assert app.gesture_name == 'TestGesture'
    assert app.duration == 60
    assert not app.status
    assert app.timerLabel.text() == "01:00"


def test_start_task(app, qtbot):
    qtbot.mouseClick(app.startBtn, Qt.LeftButton)
    assert not app.startBtn.isVisible()
    assert app.clock.isActive()
    assert app.timer.isActive()
    assert app.cap.isOpened()

    # Simulate timer timeout
    QTest.qWait(2000)  # Wait for 2 seconds
    assert app.duration < 60

    app.release_webcam()
    app.clock.stop()
    app.timer.stop()

def test_show_gesture_comment(app, qtbot):
    app.show_gesture_comment(True)
    assert app.status_label.text() == "Correct Gesture!"
    assert "green" in app.status_label.styleSheet()

    app.show_gesture_comment(False)
    assert app.status_label.text() == "Wrong Gesture!"
    assert "red" in app.status_label.styleSheet()

    app.show_gesture_comment(None)
    assert app.status_label.text() == "No hand detected!"
    assert "red" in app.status_label.styleSheet()

def test_fail_task(app):
    app.fail_task()
    assert app.status_label.text() == "Task Failed!"
    assert "red" in app.status_label.styleSheet()

def test_back_to_main(app, qtbot):
    app.status = False
    app.duration = 30
    app.fail_task()
    app.backToMain()
    # Assuming the callback prints the following:
    assert app.status_label.text() == "Task Failed!"
    assert "red" in app.status_label.styleSheet()

def test_release_webcam(app):
    app.recognitionTask()
    assert app.cap.isOpened()
    app.release_webcam()
    assert not app.cap.isOpened()
