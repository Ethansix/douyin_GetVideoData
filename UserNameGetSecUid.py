# 根据给出的的抖音用户名称，搜索得到用户对应的用户主页ID
from selenium import webdriver
import time
import pandas as pd
import urllib
from selenium.webdriver.chrome.options import Options

if __name__ == '__main__':
    df = pd.read_excel('data.xlsx', header=0)  # 导入抖音账号名信息
    name = df.iloc[:, 1]
    begin = 'https://www.douyin.com/search/'
    end = '?source=switch_tab&type=user'

    browser = webdriver.Chrome()

    hrefdata = []

    # 提前滑动验证几次
    for i in range(3):
        url = 'https://www.douyin.com/search/%E9%80%9A%E5%9F%8E%E5%8E%BF%E8%9E%8D%E5%AA%92%E4%BD%93%E4%B8%AD%E5%BF%83?source=switch_tab&type=user'
        browser.get(url)
        time.sleep(5)

    for i in range(1,135):
        user_name = name[i]
        url = begin + urllib.parse.quote(user_name) + end
        browser.get(url)

        try:
            elements = browser.find_element_by_xpath("(//li[@class ='z+CDVteT vmQjJUds']//a)[1]")
        # 需要滑动验证
        except:
            try:
                time.sleep(1)
                elements = browser.find_element_by_xpath("(//li[@class ='z+CDVteT vmQjJUds']//a)[1]")
            # 没来得及滑动，再来一次
            except:
                print('error')
                time.sleep(10)
                elements = browser.find_element_by_xpath("(//li[@class ='z+CDVteT vmQjJUds']//a)[1]")

        href = elements.get_attribute('href')

        a = href.split('?')
        print(a[0])
        b = a.split('https://www.douyin.com/video/')
        hrefdata.append(b[1])

    f = open("SecUid.txt", "w")
    for line in hrefdata:
        f.write(line + '\n')
    f.close()
