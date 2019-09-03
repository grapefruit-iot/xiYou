#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("./pinyin2hanzi")
import platform as plat
import os

from ModelSpeech_0 import modelClass
from keras import backend as K
from pinyin2hanzi import hmm

def extract( in_str):
    return [i[:-1] for i in in_str]

if __name__ == '__main__':

    if len(sys.argv) >= 2 :
        wav_name = sys.argv[1]
    else :
        wav_name = "D4_752.wav"

    datapath = ''
    modelpath = 'model_speech'

    os.environ["CUDA_VISIBLE_DEVICES"] = "4, 5, 6"

    datapath = 'dataset'
    modelpath = modelpath + '/'

    ms = modelClass(datapath)
    ms.load(modelpath + 'best.model')
    r = ms.getDataFromFile(wav_name)
    # K.clear_session()
    print('result_a：\n',r)

    ml = hmm.Hmm()
    results = ml.py2hz(extract(r))
    result = results[0]
    print('result_b：\n',result.path)

    r = ms.getDataFromFile(wav_name)
    # K.clear_session()
    results = ml.py2hz(extract(r))
    result = results[0]
    print('result_b：\n',result.path)

