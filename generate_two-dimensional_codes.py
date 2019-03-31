import requests
from selenium import webdriver
import time
from urllib import request
from PIL import Image
import os


def get_dim(html_url, name):
    url = 'http://www.liantu.com/'
    driver_path = '/Users/liudianjun/Desktop/chromedriver/chromedriver'
    driver = webdriver.Chrome(driver_path)
    driver.get(url=url)
    time.sleep(2)
    # 找到文本框位置
    text_qrtext = driver.find_element_by_id('text_text')
    # 文本框里填入数据
    text_qrtext.send_keys(html_url)
    # 找到生成二维码按钮
    # button = driver.find_element_by_id('wwei_qrcode_create')
    # 点击生成
    # print(button.get_attribute('id'))
    # button.click()
    # 设置延时等待生成二维码
    time.sleep(2)
    # 获取保存按钮
    # save_button = driver.find_element_by_id('savepng')
    # print(save_button.click())

    # 获取二维码链接
    # page_source = driver.page_source
    # img_element = driver.find_element_by_id('qrcodeimg')
    # dim_url = img_element.get_attribute('src')
    # dim_img = request.urlretrieve(dim_url, '二维码.png')
    # 根据标签截图
    # 全图截屏
    driver.save_screenshot('/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/screenshot/capture.png')
    # # 获取element
    canvas = driver.find_element_by_id('canvas')
    # # 获取元素位置信息
    # left = canvas.location['x']
    # top = canvas.location['y']
    # right = top + canvas.size['width']
    # bottom = left + canvas.size['height']
    # # 根据坐标截图
    im = Image.open('/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/screenshot/capture.png')
    im = im.crop((1411, 132, 1411+600, 132+600))  # 元素裁剪
    im.save('/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/dim_file/' + name + '.png')
    # 1411 132

    # print(canvas.location)
    # print(dim_url)
    time.sleep(3)
    driver.close()


def get_html_file_name():
    file_path = '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/Mobile-AutoBookmark'
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[1] == '.html' and 'template' not in os.path.splitext(file)[0]:
                name = os.path.splitext(file)[0]
                html_url = 'http://www.ldj.mobi/flora/{}.html'.format(name)
                get_dim(html_url, name)
                print(html_url, file)
                time.sleep(1)


if __name__ == '__main__':

    get_html_file_name()