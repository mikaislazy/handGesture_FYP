import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QToolTip
from PyQt5.QtGui import QCursor
import pyqtgraph as pg
from UserData import db_utils 
from gesture_constants import GESTURES  

class userPerformanceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        # initialize the database if it is empty
        db_utils.create_db()

        
        # layout for score and duration
        layout_score_duration = QHBoxLayout()
        colors = ['b', 'g', 'r', 'c', 'm', 'grey', 'k', 'orange', 'purple']

        # Chart 1: Score of Each Gesture in Each Trial
        self.plot1 = pg.PlotWidget(title="Score of Knowledge Task in Each Trial for All Gestures")
        self.plot1.setBackground("w")
        self.plot1.addLegend(offset=(-1, 1))  # top-left corner line label

        for i, gesture in enumerate(GESTURES):
            scores_task1 = db_utils.retrieve_gesture_score_task1(gesture)
            x = scores_task1.index + 1
            y = scores_task1['score']
            # line chart
            self.plot1.plot(x, y, pen=pg.mkPen(color=colors[i], width=2), symbol=None, name=gesture)
            #scatter chart for hovering
            scatter = pg.ScatterPlotItem(x=x, y=y, pen=pg.mkPen(None), brush=pg.mkBrush(colors[i]))
            scatter.sigClicked.connect(self.create_tooltip_callback(gesture))
            self.plot1.addItem(scatter)

        self.plot1.getPlotItem().getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(1, max([len(db_utils.retrieve_gesture_score_task1(g)) for g in GESTURES]) + 1)]])
        self.plot1.setLabel('left', 'Score')
        self.plot1.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(self.plot1)

        # Chart 2: Duration of Recognition Task in Each Trial
        self.plot2 = pg.PlotWidget(title="Duration of Recognition Task in Each Trial for All Gestures")
        self.plot2.setBackground("w")
        self.plot2.addLegend(offset=(-1, 1))  # top-left corner line label

        for i, gesture in enumerate(GESTURES):
            durations_task2 = db_utils.retrieve_gesture_duration_task2(gesture)
            x = durations_task2.index + 1
            y = durations_task2['duration']

            self.plot2.plot(x, y, pen=pg.mkPen(color=colors[i], width=2), symbol=None, name=gesture)
            scatter = pg.ScatterPlotItem(x=x, y=y, pen=pg.mkPen(None), brush=pg.mkBrush(colors[i]))
            scatter.sigClicked.connect(self.create_tooltip_callback(gesture))
            self.plot2.addItem(scatter)

        self.plot2.getPlotItem().getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(1, max([len(db_utils.retrieve_gesture_duration_task2(g)) for g in GESTURES]) + 1)]])
        self.plot2.setLabel('left', 'Duration (s)')
        self.plot2.setLabel('bottom', 'Trial')
        layout_score_duration.addWidget(self.plot2)

        # layout for error rate
        layout_error_rate = QHBoxLayout()

        # Chart 3: Error Rate of Knowledge Task"
        self.plot3 = pg.PlotWidget(title="Error Rate of Knowledge Task")
        self.plot3.setBackground("w")
        self.plot3.addLegend(offset=(-1, 1))  # top-left corner line label

        for i, gesture in enumerate(GESTURES):
            error_rates = db_utils.calculate_error_rate_task1(gesture)
            if error_rates:
                x = range(1, len(error_rates) + 1)
                y = error_rates

                self.plot3.plot(x, y, pen=pg.mkPen(color=colors[i], width=2), symbol=None, name=gesture)
                scatter = pg.ScatterPlotItem(x=x, y=y, pen=pg.mkPen(None), brush=pg.mkBrush(colors[i]))
                scatter.sigClicked.connect(self.create_tooltip_callback(gesture))
                self.plot3.addItem(scatter)
        # if min([len(db_utils.calculate_error_rate_task1(g)) for g in GESTURES]) > 0:        
        self.plot3.getPlotItem().getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(1, max([len(db_utils.calculate_error_rate_task1(g)) for g in GESTURES]) + 1)]])
        self.plot3.setLabel('left', 'Error Rate')
        self.plot3.setLabel('bottom', 'Trial')
        layout_error_rate.addWidget(self.plot3)

        # Chart 4: Error Rate of Recognition Task
        self.plot4 = pg.PlotWidget(title="Error Rate of Recognition Task")
        self.plot4.setBackground("w")
        self.plot4.addLegend(offset=(-1, 1))

        for i, gesture in enumerate(GESTURES):
            error_rates = db_utils.calculate_error_rate_task2(gesture)
            if error_rates:
                x = range(1, len(error_rates) + 1)
                y = error_rates

                self.plot4.plot(x, y, pen=pg.mkPen(color=colors[i], width=2), symbol=None, name=gesture)
                scatter = pg.ScatterPlotItem(x=x, y=y, pen=pg.mkPen(None), brush=pg.mkBrush(colors[i]))
                scatter.sigClicked.connect(self.create_tooltip_callback(gesture))
                self.plot4.addItem(scatter)
        self.plot4.getPlotItem().getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(1, max([len(db_utils.calculate_error_rate_task2(g)) for g in GESTURES]) + 1)]])
        self.plot4.setLabel('left', 'Error Rate')
        self.plot4.setLabel('bottom', 'Trial')
        layout_error_rate.addWidget(self.plot4)

        self.layout.addLayout(layout_score_duration)
        self.layout.addLayout(layout_error_rate)
        
        self.setLayout(self.layout)

    def create_tooltip_callback(self, gesture):
        return lambda _, points: self.show_tooltip(points, gesture)

    def show_tooltip(self, points, gesture):
        point = points[0]  # We only need the first point for the tooltip
        pos = point.pos()
        data = f"Value: {pos.y():.2f}\nLabel: {gesture}"
        QToolTip.showText(QCursor.pos(), data)
