# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1074, 747)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start_but = QtWidgets.QPushButton(self.centralwidget)
        self.start_but.setGeometry(QtCore.QRect(20, 590, 101, 91))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(20)
        self.start_but.setFont(font)
        self.start_but.setObjectName("start_but")
        self.stop_but = QtWidgets.QPushButton(self.centralwidget)
        self.stop_but.setGeometry(QtCore.QRect(200, 590, 101, 91))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(20)
        self.stop_but.setFont(font)
        self.stop_but.setObjectName("stop_but")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(390, 10, 681, 721))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.sentence_box = QtWidgets.QTextBrowser(self.groupBox)
        self.sentence_box.setGeometry(QtCore.QRect(10, 10, 661, 521))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        self.sentence_box.setFont(font)
        self.sentence_box.setReadOnly(False)
        self.sentence_box.setObjectName("sentence_box")
        self.keyword_box = QtWidgets.QTextBrowser(self.groupBox)
        self.keyword_box.setGeometry(QtCore.QRect(160, 570, 511, 121))
        self.keyword_box.setObjectName("keyword_box")
        self.keyword_but = QtWidgets.QPushButton(self.centralwidget)
        self.keyword_but.setGeometry(QtCore.QRect(420, 590, 101, 91))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(16)
        self.keyword_but.setFont(font)
        self.keyword_but.setObjectName("keyword_but")
        self.status_label = QtWidgets.QLabel(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(20, 700, 161, 16))
        self.status_label.setObjectName("status_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1074, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start_but.setText(_translate("MainWindow", "Start"))
        self.stop_but.setText(_translate("MainWindow", "Stop"))
        self.sentence_box.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'SimSun\';\"><br /></p></body></html>"))
        self.keyword_box.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p></body></html>"))
        self.keyword_but.setText(_translate("MainWindow", "kerword"))
        self.status_label.setText(_translate("MainWindow", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

