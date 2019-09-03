# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 16:14:17 2019

@author: Administrator
"""
'''
Python接口测试之Requests（七） https://www.cnblogs.com/weke/articles/6309044.html
'''
import requests
import json


#resualt=requests.post(
#    url='http://m.cyw.com/index.php?m=api&c=cookie&a=setcity',
#    data={'cityId':438})
#print(result.json())  

#r=r.get('http://www.baidu.com')
#print(u'HTTP状态码:',r.status_code)
#print(u'请求的URL:',r.url)
#print(u'获取Headers:',r.headers)
#print(u'响应内容:',r.text)

    
def getok(url):
    result=requests.get(url)
    return result.text

def postok(url,data):
    data=json.dumps(data)
    # print(data,type(data))
    result=requests.post(url,json=data)
    try:
        return result.json()
    except:
        return result 
    #    return json.dumps(result.text)


'''

用例：

按钮1：
r=getok('http://localhost:5000/mine')
print(r)

按钮2：
p=postok('http://localhost:5000/transactions/new',{'author':'lubinyu', 'subject':'you are great', 'length':'333'})
print(p)

按钮3
c=getok('http://localhost:5000/chain')
print(c)

'''

if __name__ =='__main__':
    # c=getok('http://106.12.24.8:5001/chain')
    # print(c)
    p=postok('http://106.12.24.8:5001/transactions/new',{'author':'lubinyu', 'subject':'you are great', 'length':333})
    print(p)
    pass 