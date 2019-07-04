# coding: utf-8

import os
import sys
import json


# 去除音调
__removetone_dict = {
    'ā': 'a',
    'á': 'a',
    'ǎ': 'a',
    'à': 'a',
    'ē': 'e',
    'é': 'e',
    'ě': 'e',
    'è': 'e',
    'ī': 'i',
    'í': 'i',
    'ǐ': 'i',
    'ì': 'i',
    'ō': 'o',
    'ó': 'o',
    'ǒ': 'o',
    'ò': 'o',
    'ū': 'u',
    'ú': 'u',
    'ǔ': 'u',
    'ù': 'u',
    'ü': 'v',
    'ǖ': 'v',
    'ǘ': 'v',
    'ǚ': 'v',
    'ǜ': 'v',
    'ń': 'n',
    'ň': 'n',
    '': 'm',
}


def writejson(obj, filename):
    with open(filename, 'w') as outfile:
        tmp = json.dumps(obj, indent=4, sort_keys=True)
        outfile.write(tmp)

def readjson(filename):
    with open(filename, 'r') as infile:
        return json.load(infile)

def to_str(v):
    if v is None:
        return None
    elif isinstance(v, bytes):
        return v.decode('utf-8', errors='ignore')
    elif isinstance(v, str):
        return v
    else:
        return ValueError('unknown type %r' % type(v) + 'of' + v)

def is_str(v):
    return isinstance(v, str)

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def remove_tone(py):
    py = to_str(py)
    r = to_str('')
    for i in py:
        if i in __removetone_dict:
            r += __removetone_dict[i]
        else:
            r += i
    return r

def normlize_pinyin(py):
    py = remove_tone(py.lower())
    if 'ue' in py:
        return py.replace('ue', 've')
    if 'ng' == py:
        return 'en'
    return py
