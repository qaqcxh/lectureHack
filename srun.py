#!/bin/python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys,os

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')


browser = webdriver.Chrome(options=options)
browser.get("http://124.16.81.61/")

try:
    browser.find_element_by_xpath('//*[@id="logout"]')
    print('网络已连接!')
    browser.quit()
    sys.exit()
except NoSuchElementException:
    pass

username_='2020xxxxxxxxxxx'
password_='xxxxxxxxxxxxxxx'
# 输入用户名,密码
username = browser.find_element_by_xpath('//*[@id="username"]')
password = browser.find_element_by_xpath('//*[@id="password"]')
username.clear()
username.send_keys(username_)
password.clear()
password.send_keys(password_)


login_btn = browser.find_element_by_xpath('//*[@id="login-account"]')
login_btn.click()

try:
    # 页面一直循环，直到显示连接成功
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="logout"]'))
    )
    print("网络已连接!")
finally:
    browser.quit()

browser.quit()
