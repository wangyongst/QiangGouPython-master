# -*- coding: utf-8 -*-
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import random
import re
import requests
import json
import sys
from bs4 import BeautifulSoup

# 对于py2，将ascii改为utf8
reload(sys)
sys.setdefaultencoding('utf8')


class TaobaoClimber:
    def __init__(self, username, password):
        self.__session = requests.Session()
        self.__username = username
        self.__password = password

    driver = None
    action = None

    # 是否登录
    __is_logined = False

    # 淘宝账户
    __username = ""
    # 登录密码
    __password = ""
    # 登陆URL
    __login_path = "https://login.taobao.com/member/login.jhtml"
    # 抢购商口URL
    __orders_path = "https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.5.1afe21baQB0KJe&id=546408734932&skuId=3493732191297&areaId=620100&user_id=890482188&cat_id=2&is_b=1&rn=6ed71117205f1c9967cdc54e85d6cdf2"
    # requests会话
    __session = None

    def __login(self):
        # 1.登陆
        try:
            self.driver.get(self.__login_path)
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
            retry = 0
            while retry < 5:
                retry += 1
                slide_span = self.driver.find_element_by_id("nc_1_n1z")  # 取得滑块span
                self.action.click_and_hold(slide_span)  # 鼠标左键按住span
                self.action.move_by_offset(257, 0)  # 向右拖动258像素完成验证
                self.action.perform()
                time.sleep(1)
                self.action.reset_actions()  # 页面进行了刷新，需要清除action之前存储的elements
                try:
                    slide_refresh = self.driver.find_element_by_xpath(
                        "//div[@id='nocaptcha']/div/span/a")  # 页面没有滑块，而是“点击刷新再来一次”
                    slide_refresh.click()
                except exceptions.NoSuchElementException:  # 滑动成功
                    break

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

    def __get_orders_page(self):
        # 1.bs4将资源转html
        html = BeautifulSoup(self.driver.page_source, "html5lib")
        # 2.取得所有的订单div
        order_div_list = html.find_all("div", {"class": "item-mod__trade-order___2LnGB trade-order-main"})
        # 3.遍历每个订单div，获取数据
        data_array = []
        for index, order_div in enumerate(order_div_list):
            order_id = order_div.find("input", attrs={"name": "orderid"}).attrs["value"]
            order_date = order_div.find("span",
                                        attrs={"data-reactid": re.compile(r"\.0\.5\.3:.+\.0\.1\.0\.0\.0\.6")}).text
            order_buyer = order_div.find("a", attrs={"class": "buyer-mod__name___S9vit"}).text
            # 4.根据订单id组合url，请求订单对应留言
            order_message = json.loads(self.__session.get(self.__message_path + order_id).text)['tip']
            data_array.append((order_id, order_date, order_buyer, order_message))
        return data_array

    def climb(self):
        # 切换回窗口
        self.driver.switch_to_window(self.driver.window_handles[0])

        result = []

        if self.__is_logined is False:
            if self.__login() is False:
                return result
            else:
                self.__is_logined = True

        # 1.进入抢购页面
        self.driver.get(self.__orders_path)
        while True:
            # 2.获取当前页面的订单信息
            time.sleep(2)  # 两秒等待页面加载
            _orders = self.__get_orders_page()
            result.extend(_orders)
            try:
                # 3.获取下一页按钮
                next_page_li = self.driver.find_element_by_class_name("pagination-next")
                # 4.判断按钮是否可点击，否则退出循环
                next_page_li.get_attribute("class").index("pagination-disabled")
                # print_msg("到达最后一页")
                break
            except ValueError:
                # print_msg("跳转到下一页")
                print(next_page_li.find_element_by_tag_name("a").text)
                next_page_li.click()
                time.sleep(1)
            except exceptions.NoSuchElementException:
                pass
        return result
