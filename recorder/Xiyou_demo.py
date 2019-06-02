import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot , QThread ,QTimer , pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from test_ui import Ui_MainWindow
from recorder import AudioRecorder
from demo import textRank ,  Msp , getMsp 



class MspThread(QThread):
    sinOut = pyqtSignal(tuple)
    def __init__(self, audio_struct,parent=None):
        super().__init__(parent)

        self.idnum , self.audio_data = audio_struct
    
    def __del__(self):
        pass 
        # print(self.idnum ,'finished !!!!!!!!!!!!!!!!!!!1')
    
    def run(self):
        msp_thread = getMsp()
        result = msp_thread.toText(self.audio_data)
        msp_thread.logout()
        self.sinOut.emit((self.idnum , result) )
        # print('thread result ' , result )
        # self.sinOut.emit(result )


class Xiyou( QMainWindow , Ui_MainWindow):

    def __init__(self , cut_sec = 10):
        super().__init__()
        self.setupUi(self)
        self.timer = QTimer(self)
        self.status = False
        self.cut_sec = cut_sec * 1000 
        self.timer.timeout.connect(self.timer_timeout)
        self.recorder = AudioRecorder(False)
        self.status_label.setText('状态：空闲')
        self.text = []

    @pyqtSlot()
    def on_start_but_pressed(self):
        if self.status == True :
            return 
        self.status_label.setText('状态：录音中')
        self.status = True
        self.recorder.startRecord()
        print('test ok ')
        self.timer.start(self.cut_sec)



    @pyqtSlot()
    def on_stop_but_pressed(self):
        if self.status == False :
            return 
        self.status_label.setText('状态：空闲')
        self.status = False
        self.recorder.stopRecord()
        print('test 1 ')
        self.timer.stop()


    @pyqtSlot()
    def on_keyword_but_pressed(self):
        print('test key word ')
        if len(self.text) <=0:
            return 

        keywords = textRank(''.join(self.text))
        print(keywords)
        self.keyword_box.clear()
        for i , word in enumerate (keywords):
            self.keyword_box.append('({}):{} ,'.format(i+1,word))        

    @pyqtSlot()
    def timer_timeout (self):
        print ('timer time out ')
        self.timer.start(self.cut_sec)
        audio_struct  = self.recorder.cut_stream()
        print('cut idnum ',audio_struct[0])
        self.recg_thread = MspThread(audio_struct)
        self.recg_thread.sinOut.connect(self.recg_finish)
        self.recg_thread.start()


    def recg_finish(self , recg_result ):

        idnum ,result = recg_result 

        #print('result len :{}'.format(len(result)) , result )
        self.text.insert(idnum, result)
        self.sentence_box.setText(''.join(self.text))
        #print('id {}:'.format(idnum) , result )
    

if __name__ =='__main__':
    app = QApplication(sys.argv)
    ui = Xiyou()
    ui.show()
    sys.exit(app.exec_())
