#!/bin/python3

import requests
import time
import csv
import re
from login import UCASLogin
from lxml import etree
from collections import namedtuple

class WakeUp(UCASLogin):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.login()
        self.courseURL = self.sepBaseURL + '/portal/site/16/801'
        self.courses = []
        self.translation = {
            '星期一': 1,
            '星期二': 2,
            '星期三': 3,
            '星期四': 4,
            '星期五': 5,
            '星期六': 6,
            '星期日': 7,
        }

    def getCourseID(self):
        ''' 获取所有课程ID '''
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
        for element in parseRes:
            if '二' in element.text:
                courseEle = element.xpath('./following-sibling::ul//div/a')
                self.courses = [ele.attrib['href'].split('/')[-1] for ele in courseEle]


    def genCSV(self):
        self.getCourseID()
        pattern = re.compile('(\d+)')
        with open('courses.csv', 'w') as f:
            writer = csv.writer(f)
            header = ['课程名称', '星期', '开始节数', '结束节数', '老师', '地点', '周数']
            Row = namedtuple('Row', header)
            writer.writerow(header)
            for course in self.courses:
                r = self.s.get('http://jwxk.ucas.ac.cn/course/coursetime/' + course, headers=self.headers, timeout=10)
                root = etree.HTML(r.text)
                # 解析获取课程名称
                name = root.xpath('//div[@class="mc-body"]/p/text()')[0]
                name = name.split('：')[-1] 

                info = root.xpath('//div[@class="mc-body"]//tr')
                for i in range(0, len(info), 3):
                    # 解析获取上课时间
                    tableHead = info[i].findtext('th')
                    if tableHead != '上课时间':
                        print('解析失败,错误信息: 无法找到上课时间!')
                        exit(-1)
                    tableData = info[i].findtext('td')
                    week, section = tableData.split('：')
                    week = self.translation[week]
                    sections = re.findall(pattern, section)
                    sections = [int(s) for s in sections]
                    secList = []
                    lastNum = None
                    for num in sections:
                        if lastNum is None:
                            startSection = num
                        elif lastNum + 1 != num:
                            secList.append((startSection, lastNum))
                            startSection = num
                        lastNum = num
                    if lastNum and startSection:
                        secList.append((startSection, lastNum))

                    # 解析获取上课地点
                    tableHead = info[i+1].findtext('th')
                    if tableHead != '上课地点':
                        print('解析失败,错误信息: 无法找到上课地点!')
                        exit(-1)
                    position = info[i+1].findtext('td')

                    # 解析获取上课周次
                    tableHead = info[i+2].findtext('th')
                    if tableHead != '上课周次':
                        print('解析失败,错误信息: 无法找到上课周次!')
                        exit(-1)
                    duration = info[i+2].findtext('td')

                    # 写结果
                    for start,end in secList:
                        writer.writerow(Row(name, week, start, end, '', position, duration))


if __name__ == '__main__':
    webpage = WakeUp('1686157273@qq.com', 'xxxxxx').genCSV()
