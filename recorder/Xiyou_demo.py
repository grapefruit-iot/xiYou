import sys
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot , QThread ,QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from test_ui import Ui_MainWindow
from recorder import AudioRecorder


class Xiyou( QMainWindow , Ui_MainWindow):

    def __init__(self , cut_sec = 10):
        super().__init__()
        self.setupUi(self)
        self.timer = QTimer(self)
        self.status = False
        self.cut_sec = cut_sec * 1000 
        self.timer.timeout.connect(self.timer_timeout)
        self.recorder = AudioRecorder(True)
    @pyqtSlot()
    def on_start_but_pressed(self):
        if self.status == True :
            return 
        self.status = True
        self.recorder.record()
        print('test ok ')
        self.timer.start(self.cut_sec)

    @pyqtSlot()
    def on_stop_but_pressed(self):
        if self.status == False :
            return 
        self.status = False
        self.recorder.stopRecord()
        print('test 1 ')
        self.timer.stop()

    @pyqtSlot()
    def timer_timeout (self):
        print ('timer time out ')
        self.timer.start(self.cut_sec)
        self.recorder.cut_stream()
    
if __name__ =='__main__':
    app = QApplication(sys.argv)
    ui = Xiyou()
    ui.show()
    sys.exit(app.exec_())
