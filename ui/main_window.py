# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStackedWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 1000)
        MainWindow.setMinimumSize(QSize(1100, 1000))
        MainWindow.setMaximumSize(QSize(100000, 100000))
        MainWindow.setBaseSize(QSize(0, 0))
        font = QFont()
        font.setFamilies([u"Calibri"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(0, 0))
        self.centralwidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.centralwidget.setStyleSheet(u"background-color: #261347;\n"
"")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 9, -1, -1)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(1000, 600))
        self.widget.setStyleSheet(u"margin: auto;\n"
"border-radius: 15px;\n"
"background-color: #3E364D;")
        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setGeometry(QRect(30, 30, 941, 131))
        self.widget_2.setStyleSheet(u"border: 1px solid white;\n"
"border-radius: 15px;\n"
"")
        self.btnHide = QPushButton(self.widget_2)
        self.btnHide.setObjectName(u"btnHide")
        self.btnHide.setGeometry(QRect(2, 3, 506, 125))
        font1 = QFont()
        font1.setFamilies([u"Calibri"])
        font1.setPointSize(12)
        font1.setWeight(QFont.Black)
        self.btnHide.setFont(font1)
        self.btnHide.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btnHide.setStyleSheet(u"QPushButton {\n"
"    border-radius: 10px;\n"
"    border: 2px solid #333;\n"
"    color: white;\n"
"    padding: 5px;\n"
"    background-color: rgb(68, 60, 70);\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #6400E6; \n"
"}")
        self.btnHide.setCheckable(True)
        self.btnHide.setChecked(True)
        self.btnUnhide = QPushButton(self.widget_2)
        self.btnUnhide.setObjectName(u"btnUnhide")
        self.btnUnhide.setGeometry(QRect(434, 3, 506, 125))
        self.btnUnhide.setFont(font1)
        self.btnUnhide.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btnUnhide.setStyleSheet(u"QPushButton {\n"
"    border-radius: 10px;\n"
"    border: 2px solid #333;\n"
"    color: white;\n"
"    padding: 5px;\n"
"    background-color: rgb(68, 60, 70); \n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #6400E6; \n"
"}")
        self.btnUnhide.setCheckable(True)
        self.widget_3 = QWidget(self.widget)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setGeometry(QRect(30, 100, 941, 461))
        self.widget_3.setStyleSheet(u"border: 1px solid white;")
        self.stackedWidget = QStackedWidget(self.widget_3)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(40, 40, 861, 381))
        self.stackedWidget.setStyleSheet(u"padding:0;\n"
"margin: 0;\n"
"border: none;\n"
"background-color: rgba(100, 0, 230,20);")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1100, 33))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btnHide.setText(QCoreApplication.translate("MainWindow", u"Hide", None))
        self.btnUnhide.setText(QCoreApplication.translate("MainWindow", u"Unhide", None))
    # retranslateUi

