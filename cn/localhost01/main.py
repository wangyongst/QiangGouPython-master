# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver import ActionChains

from spider.taobao_climber import TaobaoClimber
from __init__ import *

if __name__ == '__main__':
    # 1.给相关对象传入账号密码
    climber = TaobaoClimber(taobao_username, taobao_password)

    # 2.实例化driver
    driver = webdriver.Firefox()  # 应将浏览器驱动放于python根目录下，且python已配置path环境变量
    action = ActionChains(driver)
    #driver.maximize_window()  # 浏览器最大化
    driver.set_page_load_timeout(delay_wait)  # 设定页面加载限制时间

    TaobaoClimber.driver = driver
    TaobaoClimber.action =  action
    # 2.1上架宝贝
    is_running = True
    while is_running:
        # 2.2爬取
        orders = climber.climb()
