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
def widget(mock_start_practice_callback, qtbot):
    widget = handGesturePracticeWidget(
        start_practice_callback=mock_start_practice_callback
    )
    qtbot.addWidget(widget)
    return widget

def test_initial_state(widget):
    assert not widget.next_btn.isEnabled()
    assert widget.gesture_order_input.text() == ""
    assert widget.selected_effect is None


def test_effect_selection(widget, qtbot):
    qtbot.mouseClick(widget.fire_effect, Qt.LeftButton)
    assert widget.selected_effect == "fire_effect"
    
    qtbot.mouseClick(widget.thunder_effect, Qt.LeftButton)
    assert widget.selected_effect == "thunder_effect"
    
    qtbot.mouseClick(widget.lighting_effect, Qt.LeftButton)
    assert widget.selected_effect == "lighting_effect"

def test_start_practice(widget, mock_start_practice_callback, qtbot):
    qtbot.keyClicks(widget.gesture_order_input, "1 2 3")
    qtbot.mouseClick(widget.fire_effect, Qt.LeftButton)
    qtbot.mouseClick(widget.next_btn, Qt.LeftButton)

    expected_gesture_names = [GESTURES[0], GESTURES[1], GESTURES[2]]
    mock_start_practice_callback.assert_called_with(expected_gesture_names, "fire_effect")

def messageBox_handler(qtbot):
    messagebox = QtWidgets.QApplication.activeWindow()
    yes_button = messagebox.button(QMessageBox.Yes)
    qtbot.mouseClick(yes_button, QtCore.Qt.LeftButton, delay=1)
    
def test_check_input_value(widget):
    with patch.object(QMessageBox, 'warning', return_value=None):
        assert widget.check_input_value("1 2 3") == True
        assert widget.check_input_value("10 11 12") == False
        assert widget.check_input_value("invalid input") == False
        assert widget.check_input_value("1 3 5") == True
        assert widget.check_input_value("") == False

def test_get_input_gesture_names(widget):
    input_gesture_order = "1 2 3"
    expected_gesture_names = [GESTURES[0], GESTURES[1], GESTURES[2]]
    assert widget.get_input_gesture_names(input_gesture_order) == expected_gesture_names

