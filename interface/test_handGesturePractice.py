import pytest
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock, patch
from handGesturePractice import handGesturePracticeWidget  # Adjust the import as needed
from tool import GESTURES


@pytest.fixture
def mock_start_practice_callback():
    return Mock()

@pytest.fixture
def app(mock_start_practice_callback, qtbot):
    test_handGesturePracticeWidget = handGesturePracticeWidget(
        start_practice_callback=mock_start_practice_callback
    )
    qtbot.addWidget(test_handGesturePracticeWidget)
    return test_handGesturePracticeWidget

def test_initial_state(app):
    assert not app.next_btn.isEnabled()
    assert app.gesture_order_input.text() == ""
    assert app.selected_effect is None


def test_effect_selection(app, qtbot):
    qtbot.mouseClick(app.fire_effect, Qt.LeftButton)
    assert app.selected_effect == "fire_effect"
    
    qtbot.mouseClick(app.thunder_effect, Qt.LeftButton)
    assert app.selected_effect == "thunder_effect"
    
    qtbot.mouseClick(app.lighting_effect, Qt.LeftButton)
    assert app.selected_effect == "lighting_effect"

def test_start_practice(app, mock_start_practice_callback, qtbot):
    qtbot.keyClicks(app.gesture_order_input, "1 2 3")
    qtbot.mouseClick(app.fire_effect, Qt.LeftButton)
    qtbot.mouseClick(app.next_btn, Qt.LeftButton)

    expected_gesture_names = [GESTURES[0], GESTURES[1], GESTURES[2]]
    mock_start_practice_callback.assert_called_with(expected_gesture_names, "fire_effect")

def messageBox_handler(qtbot):
    messagebox = QtWidgets.QApplication.activeWindow()
    yes_button = messagebox.button(QMessageBox.Yes)
    qtbot.mouseClick(yes_button, QtCore.Qt.LeftButton, delay=1)
    
def test_check_input_value(app):
    with patch.object(QMessageBox, 'warning', return_value=None):
        assert app.check_input_value("1 2 3") == True
        assert app.check_input_value("10 11 12") == False
        assert app.check_input_value("invalid input") == False
        assert app.check_input_value("1 3 5") == True
        assert app.check_input_value("") == False

def test_get_input_gesture_names(app):
    input_gesture_order = "1 2 3"
    expected_gesture_names = [GESTURES[0], GESTURES[1], GESTURES[2]]
    assert app.get_input_gesture_names(input_gesture_order) == expected_gesture_names

