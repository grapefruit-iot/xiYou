#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import wave
import numpy as np
import matplotlib.pyplot as plt  
import math
import time

from python_speech_features import mfcc
from python_speech_features import delta
from python_speech_features import logfbank

from scipy.fftpack import fft

def read_wav_data(filename):

    wav = wave.open(filename,"rb") # 打开一个wav格式的声音文件流
    
    num_channel=wav.getnchannels() # 获取声道数
    framerate=wav.getframerate() # 获取帧速率
    str_data = wav.readframes(-1) # 读取全部的帧
    wav.close() # 关闭流
    wave_data = np.fromstring(str_data, dtype = np.short) # 将声音文件数据转换为数组矩阵形式
    wave_data = wave_data.reshape(-1 , num_channel)
    wave_data = wave_data.T # 将矩阵转置
    return wave_data, framerate  


def GetFrequencyFeature3(wavsignal, fs):
    x=np.linspace(0, 400 - 1, 400, dtype = np.int64)
    w = 0.54 - 0.46 * np.cos(2 * np.pi * (x) / (400 - 1) ) # 汉明窗

    if(16000 != fs):
        raise ValueError('[Error] ASRT currently only supports wav audio files with a sampling rate of 16000 Hz, but this audio is ' + str(fs) + ' Hz. ')
    
    # wav波形 加时间窗以及时移10ms
    time_window = 25 # 单位ms
    window_length = fs / 1000 * time_window # 计算窗长度的公式，目前全部为400固定值
    
    wav_arr = np.array(wavsignal)
    #wav_length = len(wavsignal[0])
    wav_length = wav_arr.shape[1]
    
    range0_end = int(len(wavsignal[0])/fs*1000 - time_window) // 10 # 计算循环终止的位置，也就是最终生成的窗数
    data_input = np.zeros((range0_end, 200), dtype = np.float) # 用于存放最终的频率特征数据
    data_line = np.zeros((1, 400), dtype = np.float)
    
    for i in range(0, range0_end):
        p_start = i * 160
        p_end = p_start + 400
        
        data_line = wav_arr[0, p_start:p_end]
        
        data_line = data_line * w # 加窗
        
        data_line = np.abs(fft(data_line)) / wav_length
        
        
        data_input[i]=data_line[0:200] # 设置为400除以2的值（即200）是取一半数据，因为是对称的
        
    #print(data_input.shape)
    data_input = np.log(data_input + 1)
    return data_input
    
def GetFrequencyFeature4(wavsignal, fs):
    '''
    主要是用来修正3版的bug
    '''
    if(16000 != fs):
        raise ValueError('[Error] ASRT currently only supports wav audio files with a sampling rate of 16000 Hz, but this audio is ' + str(fs) + ' Hz. ')
    
    # wav波形 加时间窗以及时移10ms
    time_window = 25 # 单位ms
    window_length = fs / 1000 * time_window # 计算窗长度的公式，目前全部为400固定值
    
    wav_arr = np.array(wavsignal)
    #wav_length = len(wavsignal[0])
    wav_length = wav_arr.shape[1]
    
    range0_end = int(len(wavsignal[0])/fs*1000 - time_window) // 10 + 1 # 计算循环终止的位置，也就是最终生成的窗数
    data_input = np.zeros((range0_end, window_length // 2), dtype = np.float) # 用于存放最终的频率特征数据
    data_line = np.zeros((1, window_length), dtype = np.float)
    
    for i in range(0, range0_end):
        p_start = i * 160
        p_end = p_start + 400
        
        data_line = wav_arr[0, p_start:p_end]
        
        data_line = data_line * w # 加窗
        
        data_line = np.abs(fft(data_line)) / wav_length
        
        
        data_input[i]=data_line[0: window_length // 2] # 设置为400除以2的值（即200）是取一半数据，因为是对称的
        
    #print(data_input.shape)
    data_input = np.log(data_input + 1)
    return data_input

def wav_scale(energy):
    '''
    语音信号能量归一化
    '''
    means = energy.mean() # 均值
    var=energy.var() # 方差
    e=(energy-means)/math.sqrt(var) # 归一化能量
    return e

def wav_scale2(energy):
    '''
    语音信号能量归一化
    '''
    maxnum = max(energy)
    e = energy / maxnum
    return e

def wav_scale3(energy):
    '''
    语音信号能量归一化
    '''
    for i in range(len(energy)):
        #if i == 1:
        #	#print('wavsignal[0]:\n {:.4f}'.format(energy[1]),energy[1] is int)
        energy[i] = float(energy[i]) / 100.0
        #if i == 1:
        #	#print('wavsignal[0]:\n {:.4f}'.format(energy[1]),energy[1] is int)
    return energy
    
def wav_show(wave_data, fs): # 显示出来声音波形
    time = np.arange(0, len(wave_data)) * (1.0/fs)  # 计算声音的播放时间，单位为秒
    # 画声音波形
    #plt.subplot(211)  
    plt.plot(time, wave_data)  
    #plt.subplot(212)  
    #plt.plot(time, wave_data[1], c = "g")  
    plt.show()  

    
def get_wav_list(filename):
    '''
    读取一个wav文件列表，返回一个存储该列表的字典类型值
    ps:在数据中专门有几个文件用于存放用于训练、验证和测试的wav文件列表
    '''
    txt_obj=open(filename,'r') # 打开文件并读入
    txt_text=txt_obj.read()
    txt_lines=txt_text.split('\n') # 文本分割
    dic_filelist={} # 初始化字典
    list_wavmark=[] # 初始化wav列表
    for i in txt_lines:
        if(i!=''):
            txt_l=i.split(' ')
            dic_filelist[txt_l[0]] = txt_l[1]
            list_wavmark.append(txt_l[0])
    txt_obj.close()
    return dic_filelist,list_wavmark
    
def get_wav_symbol(filename):
    '''
    读取指定数据集中，所有wav文件对应的语音符号
    返回一个存储符号集的字典类型值
    '''
    txt_obj=open(filename,'r') # 打开文件并读入
    txt_text=txt_obj.read()
    txt_lines=txt_text.split('\n') # 文本分割
    dic_symbol_list={} # 初始化字典
    list_symbolmark=[] # 初始化symbol列表
    for i in txt_lines:
        if(i!=''):
            txt_l=i.split(' ')
            dic_symbol_list[txt_l[0]]=txt_l[1:]
            list_symbolmark.append(txt_l[0])
    txt_obj.close()
    return dic_symbol_list,list_symbolmark
    
if(__name__=='__main__'):
    
    wave_data, fs = read_wav_data("A2_0.wav")  
    
    wav_show(wave_data[0],fs)
    t0=time.time()
    freimg = GetFrequencyFeature3(wave_data,fs)
    t1=time.time()
    print('time cost:',t1-t0)
    
    freimg = freimg.T
    plt.subplot(111)
    
    plt.imshow(freimg)
    plt.colorbar(cax=None,ax=None,shrink=0.5)  
     
    plt.show() 
