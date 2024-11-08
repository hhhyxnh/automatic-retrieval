import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import os
import re
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException


import json

def save_table(html_content, EN):
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取文章的发布时间
    pub_date_tag = soup.find('meta', {'name': 'PubDate'})
    if pub_date_tag:
        pub_date = pub_date_tag.get('content').replace(" ", "_").replace(":", "_")
        print(f"文章发布时间: {pub_date}")
    else:
        pub_date = "unknown_date"
        print("未找到发布时间")

    # 构建文件名，避免重复加.txt
    file_name = f'{EN}_{pub_date}'

    # 创建保存文件的目录（如果不存在）
    if not os.path.exists(f'{EN}_text'):
        os.makedirs(f'{EN}_text')

    # 查找 class 为 'wenzhang-content' 且 id 为 'wenzhang-content' 的 div
    div_content = soup.find('div', class_='wenzhang-content', id='wenzhang-content')

    # 如果找到了目标 div，保存它的内容
    if div_content:
        div_html = str(div_content)

        # 检查文件是否已经存在
        file_path = f"./{EN}_text/{file_name}.html"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as existing_file:
                existing_content = existing_file.read()

            # 计算文件的相似度
#             similarity = calculate_similarity(existing_content, div_html)
#             print(f"相似度: {similarity * 100:.2f}%")

#             # 如果相似度大于等于97%，则覆盖
#             if similarity >= 0.5:
#                 with open(file_path, 'w', encoding='utf-8') as file:
#                     file.write(div_html)
#                     print(f"文件内容相似，已覆盖文件：{file_name}.html")
                # 否则创建新文件并在文件名后加编号
            i = 1
            new_file_path = f"./{EN}_text/{file_name}_{i}.html"
            while os.path.exists(new_file_path):
                i += 1
                new_file_path = f"./{EN}_text/{file_name}_{i}.html"
            with open(new_file_path, 'w', encoding='utf-8') as file:
                file.write(div_html)
                print(f"文件名相同，已保存为新文件：{file_name}_{i}.html")
        else:
            # 如果文件不存在，直接保存
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(div_html)
                print(f"内容已保存为 '{file_name}.html'")
    else:
        print("未找到目标内容，保存失败")


def process_(EN,CN,NUM):
    driver = webdriver.Chrome()

    # 打开CBIRC官网
    driver.get('https://www.cbirc.gov.cn/cn/view/pages/index/index.html')

    # 使用XPath点击“北京”链接

    link1 = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, f'//a[text()="{CN}"]'))
    )
    driver.execute_script("arguments[0].click();", link1)

    driver.switch_to.window(driver.window_handles[1])

    link2 = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, '//a[text()="政务信息"]'))
    )
    driver.execute_script("arguments[0].click();", link2)

    punishment_link = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, '//a[text()="行政处罚"]'))
    )
    driver.execute_script("arguments[0].click();", punishment_link)
    
    count = 0
    # process_table(EN,driver)
    for i in range(NUM):
        
        count = process_table(EN,driver,count)
        
        driver.switch_to.window(driver.window_handles[1])

        link_next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@ng-click="pager.next()"]'))
        )

        # 点击“下一页”按钮
        link_next_page.click()
        
        time.sleep(2)
    process_links(EN,driver)

    
def process_table(EN,driver,count):
    punishment_links = driver.find_elements(By.XPATH, '''
                                            //a[contains(text(), "局行政") or contains(text(), "监罚") or contains(text(), "国家金融") or contains(text(), "处罚决") or contains(text(), "处罚的") or contains(text(), "关于对") or contains(text(), "保监") or contains(text(), "银监") or contains(text(), "公开表")]
''')
    
    processed_links = set()
    for index, link in enumerate(punishment_links):
        try:
            # 获取链接的 href 属性（或者使用 get_attribute('href') 根据需要）
            while True:
                try:
                    
                    link_url = link.get_attribute('href')
                    print('正确获取')
                except :
                    pass
                if link_url :
                    break
                
                

           
            if link_url in processed_links:
                print(f"链接已处理，跳过：{link_url}")
                continue

    
            driver.execute_script("arguments[0].click();", link)
            processed_links.add(link_url)
            
            count += 1
            

                
                
        except (StaleElementReferenceException, ElementNotInteractableException) as e:
            print(f"元素不可交互，跳过当前链接。错误: {e}")
            driver.switch_to.window(driver.window_handles[1])
            
    if count > 100:
        process_links(EN,driver)
        count = 0
    return count
            
def process_links(EN,driver):
    print('开始保存')
    time.sleep(2)
    while len(driver.window_handles) > 2:

        driver.switch_to.window(driver.window_handles[-1])
        page_content = driver.page_source
        save_table(page_content, EN)
        driver.close()   
        
file_path = './regions_list.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # Convert the line from string back to tuple
        region = eval(line.strip())
        process_(*region)  # Unpack the tuple and pass as arguments to the function
