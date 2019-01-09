## server 에서 chromedriver 를 실행하기 위해, 기존의 패키지에서 webdriver.ChromeOption 을 추가하여 가져옵니다.
import os
import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys

## --headless / --disable-extensions / --no-sandbox 옵션으로 드라이버를 생성합니다.
options = ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--no-sandbox')

driver = Chrome(options = options)
driver.implicitly_wait(3)

## 앞에서와 마찬가지로 크롤링 할 url 을 특정 태그 기준으로 생성합니다.
tags_url = "https://www.instagram.com/explore/tags/"
my_tag = 'seoul'
url = tags_url + my_tag

## 더 빠른 크롤링을 위해 0.25 배율로 진행하고자 했으나, chrome.settingPrivate 을 인식하지 못해 실패하였습니다
## local 환경에서 chrome browser 를 사용하던 것에서 chromium browser 를 사용하며 문제가 생긴 것으로 보입니다.
# driver.get('chrome://settings/')
# driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.25);')

## 나머지 부분은 local 환경과 마찬가지로 크롤링을 진행합니다
driver.get(url)
elem = driver.find_element_by_tag_name('body')
link_list = []
num_of_crawling_pages = 3

pagedowns = 0
while pagedowns < num_of_crawling_pages:
    
    ## 놓치는 데이터가 없도록 크롤링 후 PAGE_DOWN 방식으로 변경하였습니다.
    time.sleep(0.5)
    links = driver.find_elements_by_css_selector('div.v1Nh3 > a')
    for i in links:
        link_list.append(i.get_attribute('href'))
        
    ## Local 환경에서 테스트 한 대로 최적화된 PAGE_DOWN 방법을 사용합니다.
    for i in range(6):
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
    
    pagedowns += 1
    print(pagedowns, '페이지 크롤링 완료')

set_link_list = list(set(link_list))
num_link_list = len(link_list)
num_set_link_list = len(set_link_list)

print('중복링크 개수', num_link_list)
print('유니크링크 개수', num_set_link_list)
print('유니크링크 / 중복링크 : ', round((num_set_link_list/num_link_list) * 100, 2), '%')
print('유니크링크 구성')
print(set_link_list[:10])

## local 환경과 다르게, chromedriver 를 종료해주지 않으면 문제가 많이 발생합니다.
## driver.quit() 을 사용하면 됩니다.
driver.quit()

## set_link_list 데이터를 csv 파일 형태로 저장하기 위해 save_list_csv 함수를 정의합니다.
def save_list_csv(mylist, tag_name):
    file_name = tag_name + '_tag_link.csv'
    with open(file_name, "w") as file:
        for line in mylist:
            file.write(line + ',\n')

## 해당 데이터를 csv 형태로 저장합니다.
save_list_csv(set_link_list, my_tag)