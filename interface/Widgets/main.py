from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLabel, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import  Qt
import sys
# import cv2
import numpy as np
import time
from mainComponents import mainWindow

def main(): 
    global imgName
    # create a GUI window 
    app = QtWidgets.QApplication(sys.argv) 
    window = mainWindow() #base
    window.show()
    sys.exit(app.exec_())  

# Calling main()		 
if __name__=="__main__": 
    main()