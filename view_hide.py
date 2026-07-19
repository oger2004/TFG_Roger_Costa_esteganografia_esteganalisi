from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from crypto.crypto_aes import aes_encrypt
from stega.stega_img import hide_message_img_save
from stega.stega_txt import hide_message_txt
from stega.stega_pdf import hide_message_pdf

import os

class ViewHide(QWidget):
    def __init__(self, main_window,parent=None):
        super().__init__(parent)
        # Initialize the main window reference
        self.main_window = main_window

        # Initialize the UI from the .ui file
        loader = QUiLoader()
        file = QFile("ui/view_hide.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        # Set the layout of the widget to the loaded UI
      #  self.view_generate = ViewHideGenerate()
      #  self.view_exists = ViewHideExists()

        # Add the views to the stacked widget
        self.ui.btnBrowse.clicked.connect(self.open_dialog)

        # Connect the radio buttons to the stacked widget
        self.ui.btnDownload.clicked.connect(self.hide_message)

    def hide_message(self):
        # Get the input values from the UI
        path_in = self.ui.path_in.text()
        base, ext = os.path.splitext(path_in)
        ext = ext.lower()

        # Check if the input file exists
        path_out = base + "_hidden" + ext
        message = self.ui.message.text()
        password = self.ui.password.text()
        mode = self.ui.encryption_method.currentText()

        # Validate the input values
        if not password.strip():
            raise ValueError("Password required")

        if not message.strip():
            raise ValueError("Message required")
        
        # Encrypt the message based on the selected mode
        key_size = None 
        if mode == "AES-128":
            key_size = 16
            message = aes_encrypt(message, password, key_size)

        elif mode == "AES-256":
            key_size = 32
            message = aes_encrypt(message, password, key_size)

        else:
            raise ValueError("Invalid cipher mode")

        try:
            # Hide the message based on the file extension
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                
                hide_message_img_save(path_in, path_out, message, password)
            # Hide the message in a text file
            elif ext == ".txt":
                
                hide_message_txt(path_in, path_out, message, password)
            # Hide the message in a PDF file
            elif ext == ".pdf":
                
                hide_message_pdf(path_in, path_out, message, password)

            else:
                raise ValueError("Formato no soportado")
    
            self.main_window.show_toast("File saved correctly", success=True)

        except Exception as e:
            self.main_window.show_toast("An error has occured", success=False)


    def open_dialog(self):
        # Open a file dialog to select a file and set the path in the input field
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file",
            "",
            "All files (*);;Images (*.png *.jpg);;Text (*.txt *.pdf)"
        )

        if path:
            self.ui.path_in.setText(path)


    def on_radio_changed(self, idx, checked):
        if checked:
            self.ui.stackedHide.setCurrentIndex(idx)