from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor  

import os

from crypto.crypto_aes import aes_decrypt
from stega.stega_img import unhide_message_img_save
from stega.stega_txt import unhide_message_txt
from stega.stega_pdf import unhide_message_pdf

class ViewUnHide(QWidget):
    def __init__(self, main_window,parent=None):
        super().__init__(parent)

        self.main_window = main_window
        # Load the UI file
        loader = QUiLoader()
        file = QFile("ui/view_unhide.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        # Set the layout
        self.path_file = None
        # Connect the buttons to their respective functions
        self.ui.btnUpload.clicked.connect(self.open_dialog)
        self.ui.btnDecode.clicked.connect(self.unhide_message)

    # Function to handle the unhide message button click
    def unhide_message(self):
        path = self.ui.path_file.text()
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        password = self.ui.password.text()

        try:
            # Check if the file is an image
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                
                message = unhide_message_img_save(path, password)
            # Check if the file is a text file
            elif ext == ".txt":
                
                message = unhide_message_txt(path, password)
            # Check if the file is a PDF
            elif ext == ".pdf":
                
                message = unhide_message_pdf(path,password)

            else:
                raise ValueError("Formato no soportado")
            # Decrypt the message using the provided password
            decrypted = aes_decrypt(message, password)
            self.ui.message.setText(decrypted)

            self.main_window.show_toast("Message obtained correctly", success=True)

        except Exception as e:
            self.main_window.show_toast("An error has occured" + str(e), success=False)


    def open_dialog(self):
        # Open a file dialog to select a file
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file",
            "",
            "All files (*);;Images (*.png *.jpg);;PDF (*.pdf);; Text (*.txt)"
        )

        if path:
            self.path_file = path

            # Update the text field with the selected file path
            self.ui.path_file.setText(path)
            ext = os.path.splitext(self.path_file)[1].lower()

            if ext in [".png", ".jpg", ".pdf"]:
                self.preview_default()
            elif ext in [".txt"]:
                self.preview_txt()

    def preview_default(self):
        # Previews the selected file in the preview label
        if not self.path_file:
            return

        pixmap = QPixmap(self.path_file)
        # Check if the pixmap is valid before scaling
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.ui.previewLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.ui.previewLabel.setPixmap(pixmap)

    def preview_txt(self):
        try:
            with open(self.path_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error uploading file:\n{e}"
        # Previews the content of a text file in the preview label
        label_size = self.ui.previewLabel.size()
        width = label_size.width()
        height = max(label_size.height(), width * 2)
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.white) 
        # Create a QPainter to draw the text onto the pixmap
        painter = QPainter(pixmap)
        painter.setPen(QColor(0, 0, 0))
        # Set a monospaced font for better readability
        font = QFont("Console", 10)
        painter.setFont(font)
        margin = 5
        # Draw the text with word wrapping
        rect = pixmap.rect().adjusted(margin, margin, -margin, -margin)
        painter.drawText(rect, Qt.TextWordWrap, content)
        painter.end()
        # Scale the pixmap to fit the label while maintaining aspect ratio
        pixmap = pixmap.scaled(
            label_size.width(), label_size.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.ui.previewLabel.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        

    
