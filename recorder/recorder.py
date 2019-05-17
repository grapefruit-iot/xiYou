import pyaudio
import wave 

from demo import getMsp

CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 1                # 声道数
RATE = 11025                # 采样率

class AudioRecorder():
    def __init__(self, isSave, filepath=None):
        self.isSave = isSave
        if isSave :
            if filepath is None :
                self.filepath = "demo.wav"
            else :
                self.filepath = filepath
        self.cut_buff = []
        self.data = []
        self.status = False


    def cut_stream(self):
        '''
        将音频流进行切分
        return  cut_id , cut_data
        cut_id : 切分序号
        cut_data : 比特流音频文件
        '''

        if len(self.data) == 0:
            print('data is empty')
            return None 

        cut_data = b''.join(self.data)
        self.cut_buff.append(cut_data )
        self.data = []
        return  len(self.cut_buff) , cut_data


    def callback(self, in_data , frame_count , time_info , status):
        self.data.append(in_data)

        return (None , pyaudio.paContinue)


    def startRecord(self ):
        '''
        异步方式开始录制声音
        '''

        if self.status == True :
            print('already recording ')
            return
            
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format = FORMAT,
                        channels =CHANNELS,
                        rate = RATE,
                        input = True , 
                        output = False , 
                        frames_per_buffer = CHUNK,
                        stream_callback = self.callback
                        )
        self.status = True
    
    def stopRecord(self):
        '''
        结束声音录制，返回切分后的声音比特流
        '''
        if self.status == False:
            return 

        self.status = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # self.frames = b''.join(frames)
        self.cut_stream()
        if self.isSave:
            wf = wave.open(self.filepath,'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.cut_buff))
            wf.close()

        return self.cut_buff

if __name__ == "__main__":
    recorder = AudioRecorder(True)
    recorder.startRecord()
    print('recorder start ok ')
    msp= getMsp()

    while True :
        a = input()
        if a == 'q':
            break 
        if a == 'c':
            i ,data = recorder.cut_stream()

            result = msp.toText(data)
            print('result ok ' , result)
    data = recorder.stopRecord()
    data = b''.join(data)
    print(len(data))

    adata = open('demo.wav' , 'rb')
    adata = adata.read()

    print( ' data len , adata len ' , len(data) , len(adata))

    print ('is equal ' ,data == adata)
