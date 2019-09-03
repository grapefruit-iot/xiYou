#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from common.get_file_dict import *
from common.get_file_wav import *
import random

class DataReader():
    
    def __init__(self, path, type ):
        
        self.datapath = path; 
        self.type = type    # {train , dev , test }
        
        self.slash = '/'
        
        if(self.slash != self.datapath[-1]): 
            self.datapath = self.datapath + self.slash
         
        self.dic_wav_thchs30 = {}
        self.dic_symbol_thchs30 = {}
        self.dic_wav_stcmds = {}
        self.dic_symbol_stcmds = {}
        
        self.symbol_num = 0 
        self.list_symbol = self.GetSymbolList() 
        self.list_wavnum=[] 
        self.list_symbolnum=[] 
        
        self.data_num = 0
        self.cur_num = 0 
        self.LoadDataList()
        
        self.order = list(range(self.data_num))
        self.wavs_data = []
    
    def LoadDataList(self):
        '''
        加载用于计算的数据列表
        参数：
            type：选取的数据集类型
                train 训练集
                dev 开发集
                test 测试集
        '''
        # 设定选取哪一项作为要使用的数据集
        if(self.type=='train'):
            wavlist_thchs30 = 'thchs30' + self.slash + 'train.wav.lst'
            wavlist_stcmds = 'st-cmds' + self.slash + 'train.wav.txt'
            symbollist_thchs30 = 'thchs30' + self.slash + 'train.syllable.txt'
            symbollist_stcmds = 'st-cmds' + self.slash + 'train.syllable.txt'
        elif(self.type=='dev'):
            wavlist_thchs30 = 'thchs30' + self.slash + 'cv.wav.lst'
            wavlist_stcmds = 'st-cmds' + self.slash + 'dev.wav.txt'
            symbollist_thchs30 = 'thchs30' + self.slash + 'cv.syllable.txt'
            symbollist_stcmds = 'st-cmds' + self.slash + 'dev.syllable.txt'
        elif(self.type=='test'):
            wavlist_thchs30 = 'thchs30' + self.slash + 'test.wav.lst'
            wavlist_stcmds = 'st-cmds' + self.slash + 'test.wav.txt'
            symbollist_thchs30 = 'thchs30' + self.slash + 'test.syllable.txt'
            symbollist_stcmds = 'st-cmds' + self.slash + 'test.syllable.txt'

        self.dic_wav_thchs30,self.list_wavnum_thchs30 = get_wav_list(self.datapath + wavlist_thchs30)
        self.dic_wav_stcmds,self.list_wavnum_stcmds = get_wav_list(self.datapath + wavlist_stcmds)
        
        self.dic_symbol_thchs30,self.list_symbolnum_thchs30 = get_wav_symbol(self.datapath + symbollist_thchs30)
        self.dic_symbol_stcmds,self.list_symbolnum_stcmds = get_wav_symbol(self.datapath + symbollist_stcmds)
        self.data_num = self.GetDataNum()
    
    def GetDataNum(self):
        '''
        获取数据的数量
        当wav数量和symbol数量一致的时候返回正确的值，否则返回-1，代表出错。
        '''
        num_wavlist_thchs30 = len(self.dic_wav_thchs30)
        num_symbollist_thchs30 = len(self.dic_symbol_thchs30)
        num_wavlist_stcmds = len(self.dic_wav_stcmds)
        num_symbollist_stcmds = len(self.dic_symbol_stcmds)
        if(num_wavlist_thchs30 == num_symbollist_thchs30 and num_wavlist_stcmds == num_symbollist_stcmds):
            data_num = num_wavlist_thchs30 + num_wavlist_stcmds
        else:
            data_num = -1
        
        return data_num
         
    def GetData(self,n_start):

        weight = 2
        if(self.type=='train'):
            weight = 11


        if(n_start % weight == 0):
            filename = self.dic_wav_thchs30[self.list_wavnum_thchs30[n_start // weight]]
            list_symbol=self.dic_symbol_thchs30[self.list_symbolnum_thchs30[n_start // weight]]
        else:
            n = n_start // weight * (weight - 1)
            yushu = n_start % weight
            length=len(self.list_wavnum_stcmds)
            filename = self.dic_wav_stcmds[self.list_wavnum_stcmds[(n + yushu - 1)%length]]
            list_symbol=self.dic_symbol_stcmds[self.list_symbolnum_stcmds[(n + yushu - 1)%length]]
        
        wavsignal,fs=read_wav_data(self.datapath + filename)
        
        feat_out=[]
        for i in list_symbol:
            if(''!=i):
                n=self.SymbolToNum(i)
                feat_out.append(n)
        
        data_in = GetFrequencyFeature3(wavsignal,fs)
        
        data_in = data_in.reshape(data_in.shape[0],data_in.shape[1],1)
        
        data_label = np.array(feat_out)
        return data_in, data_label
    
    def data_genetator(self, batch_size=32, audio_length = 1600):
        

        labels = np.zeros((batch_size,1), dtype = np.float)
        while True:
            wav_batch = np.zeros((batch_size, audio_length, 200, 1), dtype = np.float)
            label_bacth = np.zeros((batch_size, 64), dtype=np.int16)
            
            wav_length = []
            label_length = []
            
            
            for i in range(batch_size):
                
                data_in, labels_in = self.GetData(self.order[self.cur_num])  # 通过随机数取一个数据
                self.cur_num +=1 
                if self.cur_num >= self.data_num :
                    self.cur_num = 0 
                    random.shuffle(self.order)
                
                wav_length.append(data_in.shape[0] //8 + data_in.shape[0] % 8)
                
                wav_batch[i,0:len(data_in)] = data_in
                label_bacth[i,0:len(labels_in)] = labels_in
                label_length.append([len(labels_in)])
            
            label_length = np.matrix(label_length)
            wav_length = np.array([wav_length]).T
            
            yield [wav_batch, label_bacth, wav_length, label_length ], labels
        
    def GetSymbolList(self):

        txt_file=open('dict.txt','r',encoding='UTF-8') 
        txt_text=txt_file.read()
        txt_lines=txt_text.split('\n') 
        list_symbol=[] 
        for i in txt_lines:
            if(i!=''):
                txt_l=i.split('\t')
                list_symbol.append(txt_l[0])
        txt_file.close()
        list_symbol.append('_')
        self.symbol_num = len(list_symbol)
        return list_symbol

    def SymbolToNum(self,symbol):
        '''
        符号转为数字
        '''
        if(symbol != ''):
            return self.list_symbol.index(symbol)
        return self.symbol_num
    
   
if(__name__=='__main__'):

    pass
    