# -*- coding: utf-8 -*-
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import random
import re
import requests
from random import choice
import sys
from bs4 import BeautifulSoup
from cn.config import *

# 对于py2，将ascii改为utf8
reload(sys)
sys.setdefaultencoding('utf8')


class TaobaoClimber:
    def __init__(self, username, password):
        self.__session = requests.Session()
        self.__username = username
        self.__password = password

    # driver = webdriver.Firefox()
    driver = None
    action = None

    # 是否登录
    __is_logined = False

    # 淘宝账户
    __username = ""
    # 登录密码
    __password = ""
    # requests会话
    __session = None

    def __login(self):
        # 1.登陆
        try:
            self.driver.get(login_path)
        except exceptions.TimeoutException:  # 当页面加载时间超过设定时间，JS来停止加载
            self.driver.execute_script('window.stop()')

        count = 0
        while count < 5:  # 重试5次
            count += 1
            if self.__login_one() is True:
                break
        if count == 5:
            return False

        # 2.保存cookies
        # driver.switch_to_default_content() #需要返回主页面，不然获取的cookies不是登陆后cookies
        list_cookies = self.driver.get_cookies()
        cookies = {}
        for s in list_cookies:
            cookies[s['name']] = s['value']
            requests.utils.add_dict_to_cookiejar(self.__session.cookies, cookies)  # 将获取的cookies设置到session
        return True

    def __login_one(self):
        try:
            # 1.点击密码登录，切换到密码登录模式 默认是二维码登录
            username_login_btn = self.driver.find_element_by_xpath("//a[@class='forget-pwd J_Quick2Static']")
            if username_login_btn.is_displayed() is True:
                username_login_btn.click()
        except exceptions.ElementNotInteractableException:
            pass

        # 2.获取账户、密码输入框
        username_input = self.driver.find_element_by_id("TPL_username_1")
        password_input = self.driver.find_element_by_id("TPL_password_1")
        # 3.为账户、密码赋值
        username_input.clear()
        # 随机点击，防止淘宝判断机器人操作而出现滑块验证
        self.action.move_by_offset(random.randint(10, 60), random.randint(10, 90)).perform()
        username_input.send_keys(self.__username)
        # 随机点击，防止淘宝判断机器人操作而出现滑块验证
        self.action.move_by_offset(random.randint(10, 60), random.randint(10, 90)).perform()
        password_input.send_keys(self.__password)
        # 4.取得滑块所在div，判断是否display 一般首次登陆不需要滑块验证
        slide_div = self.driver.find_element_by_id("nocaptcha")
        if slide_div.is_displayed() is True:
            time.sleep(10);
        # 5.获取登陆按钮，并点击登录
        submit_btn = self.driver.find_element_by_id("J_SubmitStatic")
        submit_btn.click()
        # 6.根据提示判断是否登录成功
        try:
            message = self.driver.find_element_by_id("J_Message").find_element_by_class_name("error")
            if message.text == u"为了你的账户安全，请拖动滑块完成验证":
                return False
        except exceptions.NoSuchElementException:
            pass
        # 7.有时检测当前环境是否异常，此时休眠一段时间让它检测
        try:
            self.driver.find_element_by_id("layout-center")
        except exceptions.NoSuchElementException:
            time.sleep(9)
        return True

    def climb(self):
        # 切换回窗口
        self.driver.switch_to_window(self.driver.window_handles[0])
        result = False
        if self.__is_logined is False:
            if self.__login() is False:
                return result
            else:
                self.__is_logined = True
        # 1.进入抢购页面
        self.driver.get(orders_path)
        while True:
            # 2.获取当前页面的信息
            buy = None;
            while not buy:
                buy = self.driver.find_element_by_id("J_LinkBuy");
            buy.click();
            chimas = None
            my_chi_ma = choice(chi_ma);
            while not chimas:
                chimas = self.driver.find_elements_by_xpath("//ul[@class='tm-clear J_TSaleProp     ']/li")
            for chima in chimas:
                if (chima.text == my_chi_ma and chima.get_attribute("class") != "tb-selected"):
                    chima.click();
            yanses = None;
            my_yan_se = choice(yan_se)
            while not yanses:
                yanses = self.driver.find_elements_by_xpath("//ul[@class='tm-clear J_TSaleProp tb-img     ']/li")
                for yanse in yanses:
                    if (yanse.get_attribute("title") == my_yan_se and yanse.get_attribute("class") != "tb-selected"):
                        yanse.click();
            buy.click();
            submit = None
            while not submit:
                try:
                    submit = self.driver.find_element_by_id("submitOrder_1")
                except exceptions.NoSuchElementException:
                    submit = None;
            submit.find_element_by_tag_name("a").click();
            return result
        return result
