"""
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import os

class ViewHideExists(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        loader = QUiLoader()
        file = QFile("ui/view_hide_exist.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.ui.btnBrowse.clicked.connect(self.open_dialog)

    def open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file",
            "",
            "All files (*);;Images (*.png *.jpg);;Text (*.txt *.pdf)"
        )

        if path:
            name = os.path.basename(path)
            self.ui.path_in.setText(name)

"""