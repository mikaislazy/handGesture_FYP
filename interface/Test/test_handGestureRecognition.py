import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
from handGestureRecognition import handGestureRecognitionWidget
from unittest.mock import Mock

# Fixture to create a mock function of insert_record_task2_callback
@pytest.fixture
def mock_insert_record_task2_callback():
    return Mock()

# Fixture to create a temporary widget for testing
@pytest.fixture
def app(mock_insert_record_task2_callback, qtbot):
    test_handGestureRecognitionWidget = handGestureRecognitionWidget('TestGesture', mock_insert_record_task2_callback, "Method of TestGesture")
    qtbot.addWidget(test_handGestureRecognitionWidget)
    return test_handGestureRecognitionWidget

# Testing the initial state of the widget
def test_initial_state(app):
    assert app.gesture_name == 'TestGesture'
    assert app.duration == 60
    assert not app.status
    assert app.timerLabel.text() == "01:00"

# Test the start button and its associated behavior
def test_start_task(app, qtbot):
    qtbot.mouseClick(app.start_btn, Qt.LeftButton)
    assert not app.start_btn.isVisible()
    assert app.clock.isActive()
    assert app.timer.isActive()
    assert app.cap.isOpened()

    # Simulate timer timeout
    QTest.qWait(2000)  # Wait for 2 seconds
    assert app.duration < 60

    app.release_webcam()
    app.clock.stop()
    app.timer.stop()

# Test the comment of user hand gesture
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

# Test the status_label of fail task
def test_fail_task(app):
    app.fail_task()
    assert app.status_label.text() == "Task Failed!"
    assert "red" in app.status_label.styleSheet()


# Test the release webcam function
def test_release_webcam(app):
    app.recognition_task()
    assert app.cap.isOpened()
    app.release_webcam()
    assert not app.cap.isOpened()
