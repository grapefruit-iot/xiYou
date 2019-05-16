import pyaudio
import wave 

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
        self.need_cut = False 
        self.cut_buff = []
        self.data = []
        self.status = False

    def cut_stream(self):
        self.need_cut = False 
        self.cut_buff.append( b''.join(self.data))
        self.data = []
        print(len(self.cut_buff[-1]))
        print('cut !!')


    def callback(self, in_data , frame_count , time_info , status):
        self.data.append(in_data)
        if self.need_cut :
            self.cut_stream()
        return (None , pyaudio.paContinue)


    def record(self ):
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
        # frames = []

        # for i in range(0,int(RATE/CHUNK * record_seconds)):
        #     data = stream.read(CHUNK)
        #     frames.append(data)
    
    def stopRecord(self):
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
    recorder.record()

    while True :
        a = input()
        if a == 'q':
            break 
        if a == 'c':
            recorder.cut_stream()
    data = recorder.stopRecord()


    print(len(data))
    print(len(b''.join(data)))