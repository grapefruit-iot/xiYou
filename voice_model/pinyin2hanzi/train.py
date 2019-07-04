# coding: utf-8

import os
import sys
import util
from util import readjson,writejson


BASE_START = './data/base_start.json'
BASE_EMISSION = './data/base_emission.json'
BASE_TRANSITION = './data/base_transition.json'

PY2HZ = './data/pinyin2hanzi.txt'
HZ2PY = './data/hanzi2pinyin.txt'

PY2HZ_FILE = './train/py2hz.json'
START_FILE = './train/start.json'
EMISSION_FILE = './train/emission.json'
TRANSITION_FILE = './train/transition.json'

PY_NUM = 411
HZ_NUM = 20903

def gen_py2hz():
    data = {}
    # with open(PY2HZ,encoding = 'utf-8') as infile:
    if 1:
        for line in open(PY2HZ,encoding = 'utf-8'):
            line = util.to_str(line.strip())
            tmp = line.split('=')
            if len(tmp) != 2:
                raise Exception('error py2hz')
            py, hzs = tmp
            py = py.strip()
            hzs = hzs.strip()
            if len(py) > 0 and len(hzs) > 0:
                data[py] = hzs

    writejson(data,PY2HZ_FILE)

def gen_start():
    data = {'default': 1, 'data': None}
    tmp = readjson(BASE_START)
    count = HZ_NUM
    for hz in tmp:
        count += tmp[hz]
    for hz in tmp:
        tmp[hz] = tmp[hz] / count
    data['default'] = 1.0 / count
    data['data'] = tmp
    writejson(data, START_FILE)
    
def gen_emission():
    data = {'default': 1.e-200, 'data': None}
    tmp = readjson(BASE_EMISSION)
    with open(HZ2PY, encoding='utf-8') as infile:
        for line in infile:
            line = util.to_str(line.strip())
            hz, pys = line.split('=')
            py_list = [util.normlize_pinyin(py.strip()) for py in pys.split(',')]
            char_list = [hz] * len(py_list)
            for hanzi, pinyin in zip(char_list, py_list):
                tmp.setdefault(hanzi, {})
                tmp[hanzi].setdefault(pinyin, 0.)
                tmp[hanzi][pinyin] += 1
    
    for hz in tmp:
        py_sum = 0.
        for py in tmp[hz]:
            py_sum += tmp[hz][py]
        for py in tmp[hz]:
            tmp[hz][py] = tmp[hz][py] / py_sum
    
    data['data'] = tmp
    writejson(data, EMISSION_FILE)

def gen_transition():
    data = {'default': 1./HZ_NUM,'data':None}
    tmp = readjson(BASE_TRANSITION)
    for i in tmp:
        hz_sum = HZ_NUM
        for j in tmp[i]:
            hz_sum += tmp[i][j]
        for j in tmp[i]:
            tmp[i][j] = float(tmp[i][j] + 1) / hz_sum
        tmp[i]['default'] = 1./hz_sum
    data['data'] = tmp
    writejson(data,TRANSITION_FILE)

def train():
    gen_py2hz()
    gen_start()
    gen_emission()
    gen_transition()

if __name__ == '__main__':
    train()

