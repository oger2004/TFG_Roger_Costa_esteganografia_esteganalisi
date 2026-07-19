from PySide6.QtWidgets import QApplication, QMainWindow 
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile 
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer

from view_hide import ViewHide
from view_unhide import ViewUnHide

import sys 

class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        loader = QUiLoader()
        
        # Initialize the UI from the .ui file 
        file = QFile("ui/main_window.ui") 
        file.open(QFile.ReadOnly) 
        self.ui = loader.load(file) 
        file.close() 
        self.setCentralWidget(self.ui.centralWidget()) 
        # Initialize the stacked widget and views
        self.hide_view = ViewHide(self)
        self.unhide_view = ViewUnHide(self)

        # Add the views to the stacked widget
        self.ui.stackedWidget.addWidget(self.hide_view) 
        self.ui.stackedWidget.addWidget(self.unhide_view) 

        self.ui.stackedWidget.setCurrentWidget(self.hide_view)
        # Set the initial state of the buttons
        self.ui.btnHide.setChecked(True)
        self.ui.btnUnhide.setChecked(False)

        # Connect the buttons to the view selection method
        self.ui.btnHide.clicked.connect(lambda: self.select_view(self.hide_view))
        self.ui.btnUnhide.clicked.connect(lambda: self.select_view(self.unhide_view))

    def select_view(self, view):
        # Set the current view in the stacked widget and update button states
        self.ui.stackedWidget.setCurrentWidget(view)
        self.ui.btnHide.setChecked(view == self.hide_view)
        self.ui.btnUnhide.setChecked(view == self.unhide_view)

    def show_toast(self, message, success=True, duration=2500):
        # Create a QLabel to display the toast message
        label = QLabel(self)
        label.setText(message)

        # Set the style of the label based on success or error
        color = "#2ecc71" if success else "#e74c3c"
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }}
        """)
        # Set the alignment and adjust the size of the label
        label.setAlignment(Qt.AlignCenter)
        label.adjustSize()

        # Position the label in the center of the main window
        x = (self.width() - label.width()) // 2
        y = 20
        label.move(x, y)

        # Set the window flags and attributes to make the label frameless and translucent
        label.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        label.setAttribute(Qt.WA_TranslucentBackground)

        label.show()

        # Auto-desaparece
        QTimer.singleShot(duration, label.deleteLater)


if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    window = MainWindow() 
    window.resize(1100, 800) 
    window.setMinimumSize(1100, 800) 
    window.show() 
    sys.exit(app.exec())