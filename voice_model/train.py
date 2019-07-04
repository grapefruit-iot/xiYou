#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform as plat

from ModelSpeech_0 import ModelSpeech

os.environ["CUDA_VISIBLE_DEVICES"] = "4, 5, 6"

datapath = None
modelpath = 'model_speech'

if	not os.path.exists(modelpath): # 判断保存模型的目录是否存在
	os.makedirs(modelpath) # 如果不存在，就新建一个，避免之后保存模型的时候炸掉

datapath = 'dataset'
modelpath = modelpath + '/'

ms = modelClass(datapath)

ms.load(modelpath + 'best.model')
ms.startTrain(datapath, epoch = 50, batch_size = 32, save_step = 500)

#ms.TestModel(ms.datapath, str_dataset='train', data_count = 1280)
#ms.TestModel(ms.datapath, str_dataset='test', data_count = 1280)
