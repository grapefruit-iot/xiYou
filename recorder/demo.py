from ctypes import *
import jieba.analyse
import time 

MSP_AUDIO_SAMPLE_FIRST = 1
MSP_AUDIO_SAMPLE_CONTINUE = 2
MSP_AUDIO_SAMPLE_LAST = 4
MSP_REC_STATUS_COMPLETE = 5

FRAME_LEN = 640  # Byte
MSP_SUCCESS = 0

MSP_EP_LOOKING_FOR_SPEECH = 0	
MSP_EP_IN_SPEECH = 1
MSP_EP_AFTER_SPEECH = 3	
MSP_EP_TIMEOUT = 4	
MSP_EP_ERROR = 5	
MSP_EP_MAX_SPEECH = 6

MSP_REC_STATUS_SUCCESS = 0	
MSP_REC_STATUS_NO_MATCH = 1	
MSP_REC_STATUS_INCOMPLETE = 2	
MSP_REC_STATUS_COMPLETE = 5

class Msp():
	def __init__(self,dll):
		self.dll = dll 
		self.session_begin_params = b"sub = iat, domain = iat, language = zh_cn, accent = mandarin, sample_rate = 16000, result_type = plain, result_encoding = utf8"

	def login(self , login_params):
		ret = self.dll.MSPLogin(None,None,login_params)
		print("login result ->{}".format(ret))

	def isr(self,audiofile):
		ret = c_int()
		sessionID = c_voidp()
		self.dll.QISRSessionBegin.restype = c_char_p
		sessionID = self.dll.QISRSessionBegin(None,self.session_begin_params,byref(ret))
		
		piceLne = 1638*2
		epStatus = c_int()
		recogStatus = c_int()

		wavFile = open(audiofile , 'rb')

		wavData =  wavFile.read(piceLne)
		ret = self.dll.QISRAudioWrite(sessionID,wavData , len(wavData),MSP_AUDIO_SAMPLE_FIRST,
									byref(epStatus),byref(recogStatus))
		time.sleep(0.1)
		wavData = wavFile.read(piceLne)
		print(len(wavData))
		i = 0
		while wavData :
			ret = self.dll.QISRAudioWrite(sessionID,wavData,len(wavData),MSP_AUDIO_SAMPLE_CONTINUE,
									byref(epStatus),byref(recogStatus))
			i +=1
			if i%100==0:
				print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)

			if ret != MSP_SUCCESS:
				print("failed ,ret->{}".format(ret))
				break 
			if epStatus.value == MSP_EP_AFTER_SPEECH:
				print("over break ")
				break 

			wavData =wavFile.read(piceLne)
			time.sleep(0.005)

		wavFile.close()
		ret = self.dll.QISRAudioWrite(sessionID,None,0,MSP_AUDIO_SAMPLE_LAST,
									byref(epStatus),byref(recogStatus))

		result = ''
		while recogStatus.value != MSP_REC_STATUS_COMPLETE:
			ret = c_int()
			self.dll.QISRGetResult.restype = c_char_p
			retstr = self.dll.QISRGetResult(sessionID, byref(recogStatus),0 , byref(ret))

			if ret.value != MSP_SUCCESS:
				print ('get result failed ,ret->{}'.format(ret.value))
				break 
			if retstr :
				print(retstr.decode())
				result +=retstr.decode()
			time.sleep(0.1)

		return result 

	def logout(self):
		ret = self.dll.MSPLogout()
		print("logout result ->{}".format(ret))


#鍏抽敭璇嶆彁鍙� 锛� sentence涓鸿緭鍏ュ瓧绗︿覆锛堝彲甯﹀洖杞︼級锛宼opK涓哄叧閿瘝涓暟
def textRank(sentense, topK = 5):
	sentense = sentense.splitlines(False)
	sentense = "".join(sentense)
	result = jieba.analyse.textrank(sentense,topK=topK)

	return result 


if __name__ == "__main__":

	dll = cdll.LoadLibrary("./dependence/bin/msc_x64.dll")
	login_params = b"appid = 5cccfc98"
	msp = Msp(dll)
	msp.login(login_params)
	result = msp.isr('cy11.wav')
	msp.logout()
	print(result)
	
	# txtFile = open('speach.txt','r')
	# result = txtFile.read()
	result = textRank(result,5)
	print(result)
	
