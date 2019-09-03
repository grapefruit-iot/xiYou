import sys
import os 
import time
from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtCore import pyqtSlot , QThread ,QTimer , pyqtSignal, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from try3 import Ui_MainWindow
from recorder import AudioRecorder
from demo import textRank ,  Msp , getMsp 
from Config import g_config
import requests 
import json 
FREE='状态：空闲'
RECORDING='状态：录音中'
SOUND='状态:播放中'
XUNFEI=0
MODEL=1


def getok(url):
    result=requests.get(url)
    return result.text

def postok(url,data):
    data=json.dumps(data)
    # print(data,type(data))
    result=requests.post(url,json=data)
    try:
        return result.json()
    except:
        return result 

def extract( in_str):
    return [i[:-1] for i in in_str]

try:
    sys.path.append("./pinyin2hanzi")
    import platform as plat
    import os
    from ModelSpeech_0 import modelClass
    from keras import backend as K
    from pinyin2hanzi import hmm
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    modelpath = 'model_speech'

    datapath = 'dataset'
    modelpath = modelpath + '/'

    g_ms = modelClass(datapath)
    g_ms.load(modelpath + 'best.model')

    g_ml = hmm.Hmm()
    g_err_flag=False
except:
    g_err_flag=True 
    print('load model failed ')


class MspThread(QThread):
    sinOut = pyqtSignal(tuple)
    def __init__(self, audio_struct,parent=None):
        super().__init__(parent)

        self.idnum , self.audio_data, self.method = audio_struct
        

        
    def __del__(self):
        pass 
        # print(self.idnum ,'finished !!!!!!!!!!!!!!!!!!!1')
    
    # def run(self):
    #     msp_thread = getMsp()
    #     result = msp_thread.toText(self.audio_data)
    #     msp_thread.logout()
    #     self.sinOut.emit((self.idnum , result) )
    #     # print('thread result ' , result )
    #     # self.sinOut.emit(result )
    
    def run(self):
        if g_err_flag or self.method==XUNFEI:
            msp_thread = getMsp()
            result = msp_thread.toText(self.audio_data)
            msp_thread.logout()
            self.sinOut.emit((self.idnum , result) )
        else:

            # r = g_ms.getDataFromRecorder(self.audio_data)
            result=''
            try:
                print('start model ')
                r = g_ms.getDataFromFile('tmp.wav')
                print('result_a：\n',r)
                results = g_ml.py2hz(extract(r))
                result = results[0]
                result= ''.join(result.path)+','
                print('result_b：\n',result)
            except:
                print('model error ')
            self.sinOut.emit((self.idnum , result) )    
            

class Xiyou( QMainWindow , Ui_MainWindow):

    def __init__(self , cut_sec = 10):
        super().__init__()
        self.setupUi(self)
        self.timer = QTimer(self)
        self.status = False
        self.cut_sec = cut_sec * 1000 
        self.timer.timeout.connect(self.timer_timeout)
        self.recorder = AudioRecorder()
        self.setStatusLabel(FREE)
        self.text = []
        self.counter=0
        self.method=MODEL
        self.dealRoot()
        self.player = QtMultimedia.QMediaPlayer()
        print(self.getStatusLabel())
        self.tabWidget.currentChanged['int'].connect(self.tabfun)

        self.ip = g_config.get('ip','106.12.24.8:5001')
        self.port = g_config.get('port',5001)
        
    def dealRoot(self):
        self.username=g_config.get('user','user')
        root=g_config.get('root','save_root')
        self.save_dir=os.path.join(root,self.username)
        self.setWindowTitle('Xiyou-{}'.format(self.username))
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def setStatusLabel(self,text):
        self.status_label_3.setText(text)
        # self.status_label_2.setText(text)
    
    def getStatusLabel(self):
        return self.status_label_3.text()

    def getCounter(self):
        self.counter+=1
        return '{}-{}'.format(self.username,self.counter) 
    
    def tabfun(self,index):
        # pass 
        if index == 0:
            self.method=XUNFEI
            print(XUNFEI)
            # self.sentence_box.setText(self.sentence_box_2.toPlainText())
        else :
            self.method=MODEL
            print(MODEL)
            # self.sentence_box_2.setText(self.sentence_box.toPlainText())
    
    # @pyqtSlot()
    # def on_start_but_2_pressed(self):
    #     if self.status == True :
    #         return 
    #     self.clearAll()
    #     self.method= MODEL
    #     self.setStatusLabel(RECORDING)
    #     self.status = True
    #     self.recorder.startRecord()
    #     print('test ok ')
    #     self.timer.start(self.cut_sec)
    
    # @pyqtSlot()
    # def on_stop_but_2_pressed(self):
    #     self.on_stop_but_pressed()
    
    # @pyqtSlot()
    # def on_keyword_but_2_pressed(self):
    #     self.on_keyword_but_pressed()

    @pyqtSlot()
    def on_play_but_pressed(self):
        if self.status == True :
            return 

        fname, _ = QFileDialog.getOpenFileName(self.centralwidget, "选择音频文件", "./", "Sound Files (*.mp3 *.wav)")
        if fname =='':
            print('open sound file failed ')
            return 
        self.status=True 
        url = QUrl.fromLocalFile(fname)
        content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()
        self.setStatusLabel(SOUND)

    # @pyqtSlot()
    # def on_play_but_2_pressed(self):
    #     self.on_play_but_pressed()
    

    @pyqtSlot()
    def on_start_but_pressed(self):
        self.clearAll()
        if self.status == True :
            return 
        # self.method=XUNFEI
        self.setStatusLabel(RECORDING)
        self.status = True
        self.recorder.startRecord()
        print('test ok ')
        self.timer.start(self.cut_sec)

    def clearAll(self):
        self.sentence_box.clear()
        # self.sentence_box_2.clear()
        self.keyword_box.clear()
        # self.keyword_box_2.clear()

    @pyqtSlot()
    def on_stop_but_pressed(self):
        if self.status == False :
            return 
        if self.getStatusLabel()==SOUND:
            flag=False
            self.player.stop() 
        else :
            flag=True
            
        self.setStatusLabel(FREE)
        self.status = False


        # save files  
        base_name=self.getCounter()
        self.recorder.stopRecord(os.path.join(self.save_dir,base_name+'.wav'))
        file_txt=open(os.path.join(self.save_dir,base_name+'.txt'),'w')
        file_txt.write(self.sentence_box.toPlainText())
        file_txt.close()
        file_txt=open(os.path.join(self.save_dir,base_name+'-keyword'+'.txt'),'w')
        file_txt.write(self.keyword_box.toPlainText())
        file_txt.close()
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
        # self.keyword_box_2.clear()
        for i , word in enumerate (keywords):
            self.keyword_box.append('({}):{} ,'.format(i+1,word))
            # self.keyword_box_2.append('({}):{} ,'.format(i+1,word))        

    @pyqtSlot()
    def on_mine_but_pressed(self):
        result=getok('http://{}:{}/mine'.format(self.ip,self.port))
        self.blockchain_box.setText(str(result))
        
    # @pyqtSlot()
    # def on_mine_but_2_pressed(self):
    #     pass
    
    @pyqtSlot()
    def on_add_but_pressed(self):
        subject =' '.join(self.keyword_box.toPlainText().split())
        result =postok('http://{}:{}/transactions/new'.format(self.ip,self.port),{'author': self.username, 'subject': subject, 'length':len(subject)})

        self.blockchain_box.setText(str(result))
        
    
    # @pyqtSlot()
    # def on_add_but_2_pressed(self):
    #     pass 
    
    @pyqtSlot()
    def on_inquire_but_pressed(self):
        result=getok('http://{}:{}/chain'.format(self.ip,self.port))
        self.blockchain_box.setText(str(result))
        
         
    # @pyqtSlot()
    # def on_inquire_but_2_pressed(self):
    #     pass 

    @pyqtSlot()
    def timer_timeout (self):
        print ('timer time out ')
        self.timer.start(self.cut_sec)
        audio_struct  = self.recorder.cut_stream()
        print('cut idnum ',audio_struct[0])
        if self.method == XUNFEI or g_err_flag:
            self.recg_thread = MspThread([*audio_struct,XUNFEI])
            self.recg_thread.sinOut.connect(self.recg_finish)
            self.recg_thread.start()
        else :
            result=''
            try:
                print('start model ')
                r = g_ms.getDataFromFile('tmp.wav')
                print('result_a：\n',r)
                results = g_ml.py2hz(extract(r))
                result = results[0]
                result= ''.join(result.path)+','
                print('result_b：\n',result)

            except:
                print('model error ')
            self.recg_finish((audio_struct[0],result)) 


    

    def recg_finish(self , recg_result ):

        idnum ,result = recg_result 

        #print('result len :{}'.format(len(result)) , result )
        self.text.insert(idnum, result)
        if self.tabWidget.currentIndex() == 0:
            sentence=self.sentence_box.toPlainText()
        else :
            sentence=self.sentence_box.toPlainText()
        sentence+=self.text[-1]

        self.sentence_box.setText(sentence)
        # self.sentence_box_2.setText(sentence)
        # print('id {}:'.format(idnum) , result )

    
    

if __name__ =='__main__':
    app = QApplication(sys.argv)
    ui = Xiyou()
    ui.show()
    sys.exit(app.exec_())
    # t=MspThread((1,2,MODEL))
    # t.start()
    # time.sleep(1000)


