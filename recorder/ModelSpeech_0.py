#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform as plat
import os
import time

from common.get_file_wav import *
from common.get_file_dict import *
from common.func import *

# LSTM_CNN
import keras as kr
import numpy as np
import random

from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input, Reshape, BatchNormalization # , Flatten
from keras.layers import Lambda, TimeDistributed, Activation,Conv2D, MaxPooling2D #, Merge
from keras import backend as K
from keras.regularizers import l2
from keras.optimizers import SGD, Adadelta, Adam

from data_reader import DataReader

absolute_path_name = ''
ModelName='_0'

def BN_Relu(inputs,
                num_filters=16,
                kernel_size=3,
                strides=1,
                activation='relu',
                batch_normalization=True):
    conv = Conv2D(num_filters,
                  kernel_size=kernel_size,
                  strides=strides,
                  padding='same',
                  kernel_initializer='he_normal',
                  kernel_regularizer=l2(1e-4))

    x = conv(inputs)
    if batch_normalization:
        x = BatchNormalization()(x)
    if activation is not None:
        x = Activation(activation)(x)
    return x


def ResBlock(input_data, num_filters, strides =1, kernel_size = 3):

    if strides != 1 :

        y = BN_Relu(input_data, num_filters, strides= strides, kernel_size= kernel_size)
        x = BN_Relu(input_data, num_filters, kernel_size=1, strides= strides)    
        output = kr.layers.add([y , x])

    else :
        output = BN_Relu(input_data, num_filters, kernel_size=1, strides= strides) 

    return output 



class modelClass():
    def __init__(self, datapath):
        self.learning_rate = 1e-3
        self.dropout_rate = 0.3
        self.output_num = 1424
        self.label_max_string_length = 64
        self.audio_len = 1600
        self.feature_size = 200
        self._model, self.base_model = self.modelGen() 
        self.datapath = datapath
        self.slash='/'
        if(self.slash != self.datapath[-1]):
            self.datapath = self.datapath + self.slash
    
        
    def modelGen(self):
        input_data = Input(shape=(self.audio_len, self.feature_size, 1))
        layer1 = ResBlock(ResBlock(input_data, 32, 2), 32, 1)
        layer2 = ResBlock(ResBlock(layer1, 64, 2), 64, 1)
        layer3 = ResBlock(ResBlock(layer2, 128, 2), 128, 1)
        layer4 = ResBlock(ResBlock(ResBlock(layer3, 256, (1,2)), 512, (1,2)), 512, 1)
        layer5 = Dropout(self.dropout_rate)(Reshape((200 , -1))(layer4))
        layer6 = Dropout(self.dropout_rate)(Dense(128, activation="relu", use_bias=True, kernel_initializer='he_normal')(layer5))
        layer7 = Dense(self.output_num, use_bias=True, kernel_initializer='he_normal')(layer6) # 全连接层
        y_pred = Activation('softmax', name='Activation0')(layer7)
        model_data = Model(inputs = input_data, outputs = y_pred)
        labels = Input(name='the_labels', shape=[self.label_max_string_length], dtype='float32')
        inputLen = Input(name='inputLen', shape=[1], dtype='int64')
        label_length = Input(name='label_length', shape=[1], dtype='int64')
        loss_out = Lambda(self.ctc_lambda_func, output_shape=(1,), name='ctc')([y_pred, labels, inputLen, label_length])
        model = Model(inputs=[input_data, labels, inputLen, label_length], outputs=loss_out)
        #model.summary()
        model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer = Adam())
        test_func = K.function([input_data], [y_pred])
        print('Create Model Done')
        return model, model_data
        
    def ctc_lambda_func(self, args):
        y_pred, labels, inputLen, label_length = args
        y_pred = y_pred[:, :, :]
        return K.ctc_batch_cost(labels, y_pred, inputLen, label_length)
    
    def startTrain(self, datapath, epoch = 2, save_step = 1000, batchSize = 32, filename = absolute_path_name + 'model_speech/m' + ModelName + '/speech_model'+ModelName):
        data = DataSpeech(datapath, 'train')
        
        num_data = data.GetDataNum()
        
        yielddatas = data.data_genetator(batchSize, self.audio_len)
        
        for epoch in range(epoch):
            print('Epoch %d .' % epoch)
            n_step = 0
            while True:
                try:
                    print('[message] epoch %d . Have train datas %d+' %(epoch, n_step*save_step))
                    self._model.fit_generator(yielddatas, save_step)
                    n_step += 1
                except StopIteration:
                    print('[error] generator error. please check data format.')
                    break
                
                self.save()
                self.test(self.datapath, str_dataset='train', data_count = 64)
                self.test(self.datapath, str_dataset='dev', data_count = 64)
                
    def load(self, filename = absolute_path_name + 'model_speech/best.model'):
        self._model.load_weights(filename)
        self.base_model.load_weights(filename + '.base')

    def save(self, filename = absolute_path_name + 'model_speech/best'):
        self._model.save_weights(filename + '.model')
        self.base_model.save_weights(filename + '.model.base')
        self._model.save(filename + '.h5')
        self.base_model.save(filename + '.base.h5')

    def test(self, datapath='', str_dataset='dev', data_count = 32, show_ratio = True, io_step_print = 10, io_step_file = 10):
        data = DataSpeech(self.datapath, str_dataset)
        num_data = data.GetDataNum() # 获取数据的数量
        if(data_count <= 0 or data_count > num_data): # 当data_count为小于等于0或者大于测试数据量的值时，则使用全部数据来测试
            data_count = num_data
        
        try:
            ran_num = random.randint(0,num_data - 1) # 获取一个随机数
            
            words_num = 0
            word_error_num = 0
            
            nowtime = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))

            for i in range(data_count):
                inputData, data_labels = data.GetData((ran_num + i) % num_data)  # 从随机数开始连续向后取一定数量数据
                num_bias = 0
                while(inputData.shape[0] > self.audio_len):
                    print('*[Error]','wave data lenghth of num',(ran_num + i) % num_data, 'is too long.','\n A Exception raise when test Speech Model.')
                    num_bias += 1
                    inputData, data_labels = data.GetData((ran_num + i + num_bias) % num_data)  # 从随机数开始连续向后取一定数量数据
                # 数据格式出错处理 结束
                
                pre = self.predict(inputData, inputData.shape[0] // 8)
                
                words_n = data_labels.shape[0] # 获取每个句子的字数
                words_num += words_n # 把句子的总字数加上
                edit_distance = GetEditDistance(data_labels, pre) # 获取编辑距离
                if(edit_distance <= words_n): # 当编辑距离小于等于句子字数时
                    word_error_num += edit_distance # 使用编辑距离作为错误字数
                else: # 否则肯定是增加了一堆乱七八糟的奇奇怪怪的字
                    word_error_num += words_n # 就直接加句子本来的总字数就好了
                
                if((i % io_step_print == 0 or i == data_count - 1) and show_ratio == True):
                    #print('测试进度：',i,'/',data_count)
                    print('Test Count: ',i,'/',data_count)
            #print('*[测试结果] 语音识别 ' + str_dataset + ' 集语音单字错误率：', word_error_num / words_num * 100, '%')
            print('*[Test Result] Speech Recognition ' + str_dataset + ' set word error ratio: ', word_error_num / words_num * 100, '%')
            
        except StopIteration:
            print('[Error] Model Test Error. please check data format.')
    
    def predict(self, inputData, input_len):
        in_len = np.zeros((1),dtype = np.int32)
        in_len[0] = input_len       
        x_in = np.zeros((1, 1600, self.feature_size, 1), dtype=np.float)
        x_in[0, 0:len(inputData)] = inputData
        base_pred = self.base_model.predict(x = x_in)
        base_pred = base_pred[:, :, :]
        r = K.ctc_decode(base_pred, in_len, greedy = True, beam_width=100, top_paths=1)
        r1 = K.get_value(r[0][0])
        r1 = r1[0]
        return r1
    
    def getSpeechData(self, wavsignal, fs):
        inputLen = 200 
        inputData = np.array(GetFrequencyFeature3(wavsignal, fs), dtype = np.float)
        inputData = inputData.reshape(inputData.shape[0], inputData.shape[1], 1)
        list_symbol_dic = GetSymbolList('.') # 获取拼音列表
        r_str = []
        for i in self.predict(inputData, inputLen):
            r_str.append(list_symbol_dic[i])
        return r_str
        
    def getDataFromFile(self, filename):
        wavsignal,fs = read_wav_data(filename)
        print ('fs '  ,fs)
        r = self.getSpeechData(wavsignal, fs)
        print ('r len' , len(r))
        return r

    # def getDataFromRecorder(self,wavsignal):
    #     # wav = wave.open(filename,"rb") # 打开一个wav格式的声音文件流
    
    #     # num_channel=wav.getnchannels() # 获取声道数
    #     # framerate=wav.getframerate() # 获取帧速率
    #     # str_data = wav.readframes(-1) # 读取全部的帧
    #     # wav.close() # 关闭流
    #     num_channel=1
    #     wave_data = np.fromstring(wavsignal, dtype = np.short) # 将声音文件数据转换为数组矩阵形式
    #     wave_data = wave_data.reshape(-1 , num_channel)
    #     wave_data = wave_data.T # 将矩阵转置

    #     r = self.getSpeechData(wave_data,16000)
    #     return r 
    
        
    @property
    def model(self):
        return self._model


if  __name__=='__main__':
    
    datapath =  absolute_path_name + ''
    modelpath =  absolute_path_name + 'model_speech'
    
    if(not os.path.exists(modelpath)):
        os.makedirs(modelpath)

    datapath = 'dataset'
    modelpath = modelpath + '/'
    
    ms = modelClass(datapath)
    
    ms.startTrain(datapath, epoch = 50, batchSize = 16, save_step = 500)
