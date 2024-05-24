import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton, QStackedWidget, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QTime
import cv2
import os
import pyqtgraph as pg
from UserData import db_utils
from tool import GESTURES


class userPerformanceWidget(QWidget):
    def __init__(self,  parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        # initialize the database if it is empty
        db_utils.create_db()
        db_utils.populate_test_data()
        # db_utils.teardown_test_db()
        
        # plot the charts
        self.plot_chart()        
        
        self.setLayout(self.layout)
        
    def plot_chart(self):
        # layout for score and duration
        layout_score_duration = QHBoxLayout()
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']
        
        # Chart 1: Score of Each Gesture in Each Trial
        self.plot1 = pg.PlotWidget(title="Score of Task 1 in Each Trial for All Gestures")
        self.plot1.setBackground("w")
        self.plot1.addLegend(offset=(-1, 1)) # top-left corner line label
        # plot chart
        for i, gesture in enumerate(GESTURES):
            scores_task1 = db_utils.retrieve_gesture_score_task1(gesture)
            s = scores_task1["score"].tolist()
            # print(f"score task1 of {gesture}: {s}")
            self.plot1.plot(scores_task1.index + 1, scores_task1['score'], pen=pg.mkPen(color=colors[i], width=2), symbol='o', name=gesture)

        self.plot1.getPlotItem().getAxis('bottom').setTicks([[(i, str(i)) for i in range(1, max([len(db_utils.retrieve_gesture_score_task1(g)) for g in GESTURES]) + 1)]])
        self.plot1.setLabel('left', 'Score')
        self.plot1.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(self.plot1)


        # Chart 2: Duration of Task 2 in Each Trial
        self.plot2 = pg.PlotWidget(title="Duration of Task 2 in Each Trial for All Gestures")
        self.plot2.setBackground("w")
        self.plot2.addLegend(offset=(-1, 1)) # top-left corner line label
        # plot chart
        for i, gesture in enumerate(GESTURES):
            print(f"score task1 of {gesture}: {s}")
            durations_task2 = db_utils.retrieve_gesture_duration_task2(gesture)
            self.plot2.plot(durations_task2.index + 1, durations_task2['duration'], pen=pg.mkPen(color=colors[i], width=2), symbol='o', name=gesture)
        self.plot2.getPlotItem().getAxis('bottom').setTicks([[(i, str(i)) for i in range(1, max([len(db_utils.retrieve_gesture_duration_task2(g)) for g in GESTURES]) + 1)]])
        
        self.plot2.setLabel('left', 'Duration (s)')
        self.plot2.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(self.plot2)
        
        # layout for error rate
        layout_error_rate = QHBoxLayout()
        # Chart 3: Error Rate of Task 1
        # error_rate_task1 = db_utils.calculate_error_rate_task1('ZhiJiXiangYin')
        self.plot3 = pg.PlotWidget(title="Error Rate of Task 1")
        self.plot3.setBackground("w")
        self.plot3.addLegend(offset=(-1, 1)) # top-left corner line label
        for i, gesture in enumerate(GESTURES):
            error_rates = db_utils.calculate_error_rate_task1(gesture)
            if error_rates:
                self.plot3.plot(range(1, len(error_rates) + 1), error_rates, pen=pg.mkPen(color=colors[i], width=2), name=gesture)

        self.plot3.addLegend(offset=(0, 0))  # Adjust offset to place legend in top left corner
        self.plot3.setLabel('left', 'Error Rate')
        self.plot3.setLabel('bottom', 'Trial')
        layout_error_rate.addWidget(self.plot3)

        # Chart 4: Error Rate of Task 2
        self.plot4 = pg.PlotWidget(title="Error Rate of Task 2")
        self.plot4.setBackground("w")
        self.plot4.addLegend(offset=(-1, 1)) 
        for i, gesture in enumerate(GESTURES):
            error_rates = db_utils.calculate_error_rate_task2(gesture)
            if error_rates:
                self.plot4.plot(range(1, len(error_rates) + 1), error_rates, pen=pg.mkPen(color=colors[i], width=2), name=gesture)

        self.plot4.setLabel('left', 'Error Rate')
        self.plot4.setLabel('bottom', 'Gesture Name')
        layout_error_rate.addWidget(self.plot4)
        
        self.layout.addLayout(layout_score_duration)
        self.layout.addLayout(layout_error_rate)

# def main():
    
    
#     app = QApplication([])
#     chart_widget = UserPerformanceWidget()
#     chart_widget.show()
#     app.exec_()

# if __name__ == "__main__":
#     main()
        
        