# -*- coding: utf-8 -*-
import time
from selenium import webdriver
import threading
from selenium.webdriver import ActionChains
from cn.config import *

from spider.taobao_climber import TaobaoClimber
from __init__ import *


def clim(username,password):
    # 1.给相关对象传入账号密码
    climber = TaobaoClimber(username, password)

    # 2.实例化driver
    driver = webdriver.Firefox()  # 应将浏览器驱动放于python根目录下，且python已配置path环境变量
    action = ActionChains(driver)
    driver.maximize_window()  # 浏览器最大化
    driver.set_page_load_timeout(delay_wait)  # 设定页面加载限制时间

    climber.driver = driver
    climber.action =  action
    is_running = True
    while is_running:
        # 2.2抢购
        is_running = climber.climb()

if __name__ == '__main__':
     for i in username_password:
         threading.Thread(target=clim,args=(i[0],i[1])).start()




