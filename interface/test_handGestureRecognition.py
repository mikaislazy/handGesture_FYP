import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
from handGestureRecognition import handGestureRecognitionWidget

@pytest.fixture(scope="module")
def app():
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def widget(app):
    def insert_record_task2_callback(gesture_name, status, time):
        print(f"Gesture: {gesture_name}, Status: {status}, Time: {time}")
        
    widget = handGestureRecognitionWidget('TestGesture', insert_record_task2_callback)
    yield widget
    widget.close()

def test_initial_state(widget):
    assert widget.gesture_name == 'TestGesture'
    assert widget.duration == 60
    assert not widget.status
    assert widget.timerLabel.text() == "01:00"


def test_start_task(widget, qtbot):
    qtbot.mouseClick(widget.startBtn, Qt.LeftButton)
    assert not widget.startBtn.isVisible()
    assert widget.clock.isActive()
    assert widget.timer.isActive()
    assert widget.cap.isOpened()

    # Simulate timer timeout
    QTest.qWait(2000)  # Wait for 2 seconds
    assert widget.duration < 60

    widget.release_webcam()
    widget.clock.stop()
    widget.timer.stop()

def test_show_gesture_comment(widget, qtbot):
    widget.show_gesture_comment(True)
    assert widget.status_label.text() == "Correct Gesture!"
    assert "green" in widget.status_label.styleSheet()

    widget.show_gesture_comment(False)
    assert widget.status_label.text() == "Wrong Gesture!"
    assert "red" in widget.status_label.styleSheet()

    widget.show_gesture_comment(None)
    assert widget.status_label.text() == "No hand detected!"
    assert "red" in widget.status_label.styleSheet()

def test_fail_task(widget):
    widget.fail_task()
    assert widget.status_label.text() == "Task Failed!"
    assert "red" in widget.status_label.styleSheet()

def test_back_to_main(widget, qtbot):
    widget.status = False
    widget.duration = 30
    widget.fail_task()
    widget.backToMain()
    # Assuming the callback prints the following:
    assert widget.status_label.text() == "Task Failed!"
    assert "red" in widget.status_label.styleSheet()

def test_release_webcam(widget):
    widget.recognitionTask()
    assert widget.cap.isOpened()
    widget.release_webcam()
    assert not widget.cap.isOpened()
