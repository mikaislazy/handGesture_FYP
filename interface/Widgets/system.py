from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from UserData import db_utils
from PyQt5.QtWidgets import QMessageBox

class systemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Main layout
        self.layout = QVBoxLayout()
        self.setStyleSheet("""
            
            QPushButton {
            border: none; 
            background-color: #f0f0f0; 
            padding: 10px;
            text-align: left;
            font-size: 16px;
            }
            QPushButton:pressed {
            background-color: #e0e0e0; 
            }
        """)
        # Clear data button
        self.clear_btn = QPushButton("Clear Data", self)
        self.clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clear_btn.setStyleSheet(""" 
                        
            border: none;  
            background-color: #f0f0f0;
            padding: 5px;
            text-align: left;
            font-size: 16px;
            border-bottom: 1px solid black;
            """)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setMouseTracking(True)
        self.clear_btn.clicked.connect(self.clear_data)
        
        self.setLayout(self.layout)

    def clear_data(self):
        # Ask user for confirmation
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to clear the data?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db_utils.clear_db()
            # Show success message
            QMessageBox.information(self, 'Success', 'Data cleared successfully.')
        else:
            # Show cancellation message
            QMessageBox.information(self, 'Cancelled', 'Data clearing cancelled.')
        

