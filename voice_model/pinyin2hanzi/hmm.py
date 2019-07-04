# coding: utf-8

import math
import sys
from priorityset import PrioritySet
import util
import os
from util import readjson,writejson,to_str

basedir = os.path.dirname(os.path.abspath(__file__))

PY2HZ_FILE = os.path.join(basedir,'train/py2hz.json')
START_FILE = os.path.join(basedir, 'train/start.json')
EMISSION_FILE = os.path.join(basedir,'train/emission.json')
TRANSITION_FILE = os.path.join(basedir,'train/transition.json')

DATA = 'data'
DEFAULT = 'default'

min_prob = 3.14e-200

class Hmm():
    
    def __init__(self):
        self.py2hz_dict = readjson(PY2HZ_FILE)
        self.start_dict = readjson(START_FILE)
        self.emission_dict = readjson(EMISSION_FILE)
        self.trans_dict = readjson(TRANSITION_FILE)
    
    def start(self, state):
        state = to_str(state)
        data = self.start_dict[DATA]
        default = self.start_dict[DEFAULT]
        if state in data:
            return float(data[state])
        else:
            return float(default)
    
    def emission(self, state, one_pinyin):
        pinyin = to_str(one_pinyin)
        hanzi = to_str(state)

        data = self.emission_dict[DATA]
        default = self.emission_dict[DEFAULT]

        if hanzi not in data:
            return float(default)
        
        if pinyin not in data[hanzi]:
            return float(default)
        else:
            return float(data[hanzi][pinyin])
    
    def transition(self, pre_state, next_state):
        pre_state = to_str(pre_state)
        next_state = to_str(next_state)

        data = self.trans_dict[DATA]
        default = self.trans_dict[DEFAULT]

        if pre_state not in data:
            return float(default)

        if next_state in data[pre_state]:
            return float(data[pre_state][next_state])
        elif DEFAULT in data[pre_state]:
            return float(data[pre_state][DEFAULT])
        else:
            return float(default)

    def get_states(self, pinyin):
        return [hanzi for hanzi in self.py2hz_dict[pinyin]]

    def viterbi(self, pinyin_list, path_num, log):
        V = [{}]
        t = 0
        cur_py = pinyin_list[t]

        pre_states = self.get_states(cur_py)
        cur_states = pre_states
        for state in cur_states:
            if log:
                score = math.log(max(self.start(state), min_prob)) + math.log(max(self.emission(state, cur_py), min_prob))
            else:
                score = max(self.start(state), min_prob) * max(self.emission(state, cur_py), min_prob)
            
            path = [state]
            V[0].setdefault(state, PrioritySet(path_num))
            V[0][state].put(score, path)
            
        for t in range(1, len(pinyin_list)):
            cur_py = pinyin_list[t]
            
            if len(V) == 2:
                V = [V[-1]]
            V.append({})

            pre_states = cur_states
            cur_states = self.get_states(cur_py)

            for state in cur_states:
                V[1].setdefault(state, PrioritySet(path_num))
                for state0 in pre_states:
                    for item in V[0][state0]:
                        if log:
                            score = item.score + math.log(max(self.transition(state0, state), min_prob)) + math.log(max(self.emission(state, cur_py), min_prob))
                        else:
                            score = item.score * max(self.transition(state0, state), min_prob) * max(self.emission(state, cur_py), min_prob)

                        path = item.path + [state]
                        V[1][state].put(score, path)
            
            result = PrioritySet(path_num)
            for tmp in V[-1]:
                for item in V[-1][tmp]:
                    result.put(item.score, item.path)
            
        result = [item for item in result]
        result = sorted(result, key=lambda item: item.score, reverse=True)
            
        return result

    def py2hz(self, pinyin_list, path_num=5, log=False):
        return self.viterbi(pinyin_list, path_num, log)
        
if __name__ == '__main__':
    h = Hmm()
    result = h.py2hz(('chuang', 'qian', 'ming', 'yve', 'guang'))
    for item in result:
        print(item.score, ''.join(item.path))

    result = h.py2hz(('ren', 'min', 'wu', 'zhuang'),log = True)
    for item in result:
        print(item.score, ''.join(item.path))

    list = ['ta1', 'men5', 'zou3', 'dao4', 'si4', 'ma3', 'lu4', 'yi2', 'jia1', 'cha2', 'shi4', 'pu4', 'li3', 'a1', 'jiu3', 'shuo1', 'yao4', 'mai3', 'xun1', 'yu2', 'ta1', 'gei3', 'mai3', 'le5', 'you4', 'gei3', 'zhuang4', 'er2', 'mai3', 'le5', 'ding3', 'gan1']
    list = [i[:-1] for i in list]
    result = h.py2hz(list,log = True)
    for item in result:
        print(item.score, ''.join(item.path))
