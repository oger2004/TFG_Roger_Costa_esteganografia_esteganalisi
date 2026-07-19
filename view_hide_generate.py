"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class ViewHideGenerate(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        loader = QUiLoader()
        file = QFile("ui/view_hide_generate.ui")
        file.open(QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(ui)
"""