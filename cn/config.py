# -*- coding: utf-8 -*-
# 账号参数
#多个账号,账号密码配对，并以逗号隔开，外加[]
username_password=[["111111","11111"],["22222","222222"]]


# 爬虫每次检查是否可以抢购隔/秒
check_order_period = 30
# 页面加载等待最长时间（推荐10秒以上，视网速而定）
delay_wait = 15
# 登陆URL
login_path = "https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.tmall.com%2F"
# 抢购商口URL
orders_path = "https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.5.1afe21baQB0KJe&id=546408734932&skuId=3493732191297&areaId=620100&user_id=890482188&cat_id=2&is_b=1&rn=6ed71117205f1c9967cdc54e85d6cdf2"
