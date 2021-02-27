#!/bin/python3

from login import UCASLogin
from lxml import etree
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import json
import os

class Lectures(UCASLogin):
    def __init__(self, username, password):
        UCASLogin.__init__(self, username, password)
        self.login()
        self.courseURL = self.sepBaseURL + '/portal/site/16/801'

    def checkForUpdates(self, courses):
        ''' 检查课程资源是否有更新 '''
        updatedRes = []
        for semester in courses:
            if not os.path.exists(semester):
                os.mkdir(semester) # 创建一个新的学期目录
            for courseName, courseHref in courses[semester]:
                coursePath = os.path.join(semester, courseName)
                if not os.path.exists(coursePath):
                    os.mkdir(coursePath) # 创建课程目录
                # 获取最新课程资源信息
                r = self.s.get(courseHref, timeout=self.timeout)
                parseRes = etree.HTML(r.text).xpath('//li[@class="file"]/a')
                resources = [(ele.text, courseHref + '/' + ele.attrib['href']) for ele in parseRes]
                for resourceName, resourceHref in resources:
                    resourcePath = os.path.join(coursePath, resourceName)
                    if not os.path.exists(resourcePath):
                        print('正在下载资源:', resourcePath)
                        r = self.s.get(resourceHref, timeout=3600)
                        with open(resourcePath, 'wb') as f:
                            f.write(r.content)
                        updatedRes.append(resourcePath)
                        print('下载成功!    ', resourcePath)
        return updatedRes

    def collectLectures(self):
        ''' 获取所有课程的课件 '''
        # 1.解析页面获取跳转URL
        r = self.s.get(self.courseURL, timeout=self.timeout)
        parseRes = etree.HTML(r.text).xpath('//h4/a/@href')
        if len(parseRes) != 1:
            print('课程网站URL解析错误')
        else:
            self.courseURL = parseRes[0]
        # 2.跳转到课程网站
        print('正在跳转到课程网站...')
        r = self.s.get(self.courseURL, timeout=self.timeout)
        # 3.解析获取所有学期的课程
        parseRes = etree.HTML(r.text).xpath('//div[@class="moresites-left-col"]/div/h3')
        courses = {}
        if len(parseRes) == 0:
            print('当前没有任何课程')
            return False
        else:
            for element in parseRes:
                if not element.text.endswith('学期'):
                    print('当前没有任何课程')
                    return False
                courseEle = element.xpath('./following-sibling::ul//div/a')
                lecturesBaseURL = 'https://course.ucas.ac.cn/access/content/group/'
                courses[element.text] = \
                    [(ele.attrib['title'], lecturesBaseURL + ele.attrib['href'].split('/')[-1]) for ele in courseEle]

            self.message = self.checkForUpdates(courses)
            self.message = '\n'.join(self.message)
            self.s.close()

    def sendEmail(self, senderEmail, receiverEmail, senderPasswd):
        try:
            msg = MIMEText(self.message, 'plain', 'utf-8')
            msg['From'] = formataddr(('UCAS课件同步服务器', senderEmail))
            msg['To'] = formataddr(('Me', receiverEmail))
            msg['Subject'] = 'UCAS课件同步通知'

            server = smtplib.SMTP_SSL('smtp.qq.com', 465)
            server.login(senderEmail, senderPasswd)
            server.sendmail(senderEmail, receiverEmail, msg.as_string())
            server.quit()
            print('邮件发送成功!')
        except Exception:
            print('邮件发送失败!')
                        

if __name__ == '__main__':
    lec = Lectures(os.getenv('SEP_USER_NAME'), os.getenv('SEP_PASSWD'))
    lec.collectLectures()
    if lec.message != '':
        lec.sendEmail(os.getenv('SENDER_EMAIL'), os.getenv('RECEIVER_EMAIL'), os.getenv('SENDER_PASSWD'))
 

