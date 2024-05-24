import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import os
import pyqtgraph as pg

from UserData import db_utils

class userPerformanceWidget(QWidget):
     def __init__(self,  parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        db_utils.create_db()
        db_utils.populate_test_data()
        # db_utils.teardown_test_db()
        
        # layout for score and duration
        layout_score_duration = QHBoxLayout()
        # Chart 1: Score of Task 1 in Each Trial
        scores_task1 = db_utils.retrieve_gesture_score_task1('gesture1')
        plot1 = pg.PlotWidget(title="Score of Task 1 in Each Trial")
        plot1.plot(scores_task1.index + 1, scores_task1['score'], pen=pg.mkPen(color='b', width=2), symbol='o')
        plot1.setLabel('left', 'Score')
        plot1.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(plot1)

        # Chart 2: Duration of Task 2 in Each Trial
        durations_task2 = db_utils.retrieve_gesture_duration_task2('gesture1')
        plot2 = pg.PlotWidget(title="Duration of Task 2 in Each Trial")
        plot2.plot(durations_task2.index + 1, durations_task2['duration'], pen=pg.mkPen(color='g', width=2), symbol='o')
        plot2.setLabel('left', 'Duration (s)')
        plot2.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(plot2)
        
        # layout for error rate
        layout_error_rate = QHBoxLayout()
        # Chart 3: Error Rate of Task 1
        error_rate_task1 = db_utils.calculate_error_rate_task1('gesture1')
        plot3 = pg.PlotWidget(title="Error Rate of Task 1")
        plot3.plot([0, 1], [error_rate_task1, error_rate_task1], pen=pg.mkPen(color='r', width=2))
        plot3.setLabel('left', 'Error Rate')
        plot3.setLabel('bottom', 'Gesture Name')
        layout_error_rate.addWidget(plot3)

        # Chart 4: Error Rate of Task 2
        error_rate_task2 = db_utils.calculate_error_rate_task2('gesture1')
        plot4 = pg.PlotWidget(title="Error Rate of Task 2")
        plot4.plot([0, 1], [error_rate_task2, error_rate_task2], pen=pg.mkPen(color='m', width=2))
        plot4.setLabel('left', 'Error Rate')
        plot4.setLabel('bottom', 'Gesture Name')
        layout_error_rate.addWidget(plot4)
        
        layout.addLayout(layout_score_duration)
        layout.addLayout(layout_error_rate)
        
        self.setLayout(layout)

# def main():
    
    
#     app = QApplication([])
#     chart_widget = UserPerformanceWidget()
#     chart_widget.show()
#     app.exec_()

# if __name__ == "__main__":
#     main()
        
        