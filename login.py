#!/bin/python3

'''
Author: qwqcxh
Email: 1686157273@qq.com
License: Apache License 2.0
'''

import requests
import sys
import os
from lxml import etree
from PIL import Image
from io import BytesIO

# 关闭https CA认证警告
requests.packages.urllib3.disable_warnings()

class UCASLogin:
    ''' sep登录，提供onestop.ucas.ac.cn和sep.ucas.ac.cn两个入口 '''
    def __init__(self, username, password):
        ''' 初始化一些共享信息以及会话 '''
        self.username = username
        self.password = password
        self.sepBaseURL = 'http://sep.ucas.ac.cn'
        self.onestopBaseURL = 'https://onestop.ucas.ac.cn'
        self.headers = {
            "Connection": "keep-alive",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                           (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
        }
        self.timeout = 3600
        self.s = requests.Session()
        self.sepHTML = None
        
    def getVerifyCode(self):
        ''' 手工填写验证码 '''
        r = self.s.get(self.sepBaseURL + '/changePic', timeout=self.timeout)
        img = Image.open(BytesIO(r.content))
        img.show()
        return input('请输入验证码：')

    def loginBySep(self):
        ''' 通过sep.ucas.ac.cn登录sep, 校外需验证码 '''
        # 构造post请求报文
        verifyCode = self.getVerifyCode()
        data = {
            'userName': self.username,
            'pwd': self.password,
            'certCode': verifyCode,
            'sb': 'sb'
        }
        r = self.s.post(self.sepBaseURL + '/slogin', data=data, headers=self.headers, timeout=self.timeout)
        # 正确性检测，如果用户名或者密码、验证码输入有误，提示并退出
        alert = etree.HTML(r.text).xpath('//div[contains(@class, "alert-error")]/text()')
        if len(alert):
            for errorInfo in alert:
                print(errorInfo)
                return False
        else:
            self.sepHTML = r.text
            print(self.sepHTML)
            return True

    def loginByOnestop(self):
        ''' 通过onestop.ucas.ac.cn登入sep, 无需验证码 '''
        # 构造post请求报文
        data = {
            'username': self.username,
            'password': self.password,
            'remember': 'checked'
        }
        self.s.headers['X-Requested-With'] = 'XMLHttpRequest'
        r = self.s.post(self.onestopBaseURL + '/Ajax/Login/0', data=data, headers=self.headers, verify=False, timeout=self.timeout)
        if r.json().get('f') == False:
            print('登录失败，错误提示：' + r.json().get('msg'))
            print(self.username, self.password)
            return False
        else:
            self.sepHTML = self.s.get(r.json().get('msg'), timeout=self.timeout)
            return True

    def login(self):
        ''' 登录主函数 '''
        print('正在登录中...')
        if self.loginByOnestop(): # or self.loginBySep():
            print('登录成功!')
        else:
            sys.exit(1)

if __name__ == '__main__':
    UCASLogin().login(os.getenv('SEP_USER_NAME'), os.getenv('SEP_PASSWD'))

