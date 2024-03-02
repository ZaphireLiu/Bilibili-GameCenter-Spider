# %%
import os
import time
import json
import random
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# %%
''' 参数设置 '''
# 输出路径
output_path = 'output'
# 游戏页面id，即 https://www.biligame.com/detail/?id=107825 网址中id=后面的数字
game_page_id = 107825 # 测试游戏：来自星尘
# 设置Edge WebDriver的路径，如果写入环境变量则可以忽略，但需要改变后面启动WebDriver部分的参数
edge_driver_path = "PATH_TO_WEBDRIVER"
# 多少页保存一个文件
save_interval = 20

# %%
# 查找特定的元素
def locate_element(driver, method, data):
    try:
        element = driver.find_element(method, data)
        return element
    except NoSuchElementException:
        return False
    
# 找到特定元素并点击
def click_element(driver, element_xpath):
    # 等待到元素可以点击
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
    webdriver.ActionChains(driver).move_to_element(element).click(element).perform()

# %%
# 目标网页的URL
url = f'https://www.biligame.com/detail/?id={game_page_id}'
# 元素XPath，通过F12调试工具获取
comment_xpath      = '/html/body/div[1]/div[3]/div[1]/div[1]/a[2]'
more_comment_xpath = '/html/body/div[1]/div[3]/div[1]/div[2]/div[7]'
sort_newest_xpath  = '/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div[1]/a[3]'
next_page_xpath    = '/html/body/div[1]/div[3]/div[1]/div[3]/div[3]/div[11]/a[9]'
comment_area_xpath = '/html/body/div[1]/div[3]/div[1]/div[3]/div[2]'
# 设置Edge WebDriver的选项
service = Service(edge_driver_path) # 如果WebDriver写入环境变量则不需要参数
edge_options = webdriver.EdgeOptions()
edge_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
# 启动Edge WebDriver，并指定驱动路径和选项
driver = webdriver.Edge(service=service, options=edge_options)
# 加载目标网页
driver.get(url)

# %%
# 加载评论区
click_element(driver, comment_xpath)
while not locate_element(driver, By.XPATH, "//a[text()='下一页' and @href]"): 
    time.sleep(0.2)
    
# 获取评论区总页码
comment_area = locate_element(driver, By.XPATH, comment_area_xpath)
comment_area_html = comment_area.get_attribute('outerHTML')
soup = BeautifulSoup(comment_area_html, 'html.parser')
page_num = 0

for child in soup.find_all(name='a', class_=''):
    if str(child.text).isdigit():
        page_num = max(page_num, int(child.text)) 

print("总页数：", page_num)
page_nums = [n for n in range(page_num)]
cache_html = comment_area_html

# 按最新排序
click_element(driver, sort_newest_xpath)
while cache_html == comment_area_html:
    comment_area = locate_element(driver, By.XPATH, comment_area_xpath)
    cache_html   = comment_area.get_attribute('outerHTML')
    time.sleep(0.2)

# %%
# page_num = 2 # 手动设置爬取页数
digit_only = lambda text: ''.join(filter(str.isdigit, text))
comment_list = []
last_save_loc = 0
# 检测输出路径是否存在
if not os.path.exists(output_path):
    os.mkdir(output_path)
for i in range(page_num):
    start_time = time.time()
    print(f'Page {i+1} of {page_num}')
    # 保存至json文件
    if i % save_interval == 0 and len(comment_list) != 0:
        json_str = json.dumps(comment_list, indent=4)
        with open(f'{output_path}/comment_data_{last_save_loc+1}-{i}.json', 'w') as json_file:
            json_file.write(json_str)
        print(f"Dump comment_data_{last_save_loc+1}-{i}.json complete.")
        last_save_loc = i
    # 读取评论区数据
    comment_area = locate_element(driver, By.XPATH, comment_area_xpath)
    comment_area_html = comment_area.get_attribute('outerHTML')
    soup = BeautifulSoup(comment_area_html, 'html.parser')
    # 遍历本页所有评论
    for child in soup.find_all(name='div', class_='bui-comment clearfix'):
        comment = child.find(name='div', class_='comment-main')
        comment_log = {}
        comment_log['userid']     = comment.find(name='a', class_="user-name")['href'].split('/')[-2]
        comment_log['time']       = comment.find(name='footer', class_='clearfix').find(name='span', class_='')['title']
        comment_log['text']       = comment.find(name='div', class_="bui-multi-line-text").text
        comment_log['up_count']   = digit_only(comment.find(name='a', class_="up-count").text)
        comment_log['down_count'] = digit_only(comment.find(name='a', class_="down-count").text)
        comment_log['up_count']   = int(comment_log['up_count']) if len(comment_log['up_count']) > 0 else 0
        comment_log['down_count'] = int(comment_log['down_count']) if len(comment_log['down_count']) > 0 else 0
        comment_log['star_num']   = len(comment.find_all(name='svg', class_='bui-icon bui-icon-star filled'))
        comment_list.append(comment_log)
        print(comment_log['userid'], f"{comment_log['star_num']}/5", comment_log['time'])
        print(comment_log['text'])
    # 随机等待一段时间模拟用户行为防止被ban
    if time.time() - start_time > 2:
        time.sleep(random.uniform(0, 2))
    else:
        time.sleep(random.uniform(1, 3))
        
    # 下一页
    if i == page_num - 1: break
    next_page = locate_element(driver, By.XPATH, "//a[text()='下一页' and @href]")
    webdriver.ActionChains(driver).move_to_element(next_page).click(next_page).perform()
    cache_html = comment_area_html
    while cache_html == comment_area_html: # 等待页面加载完成
        comment_area = locate_element(driver, By.XPATH, comment_area_xpath)
        cache_html   = comment_area.get_attribute('outerHTML')
        time.sleep(0.2)

# 保存最后的部分
json_str = json.dumps(comment_list, indent=4)
with open(f'{output_path}/comment_data_{last_save_loc+1}-{i+1}.json', 'w') as json_file:
    json_file.write(json_str)
print(f"Dump comment_data_{last_save_loc+1}-{i+1}.json complete.\nALL comment exported.")

driver.quit() # 关闭浏览器
        


