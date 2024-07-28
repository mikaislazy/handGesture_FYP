from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLabel, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import  Qt
import sys
import numpy as np
import time
from mainComponents import mainWindow

def main(): 
    # create a GUI window 
    app = QtWidgets.QApplication(sys.argv) 
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())  

if __name__=="__main__": 
    main()