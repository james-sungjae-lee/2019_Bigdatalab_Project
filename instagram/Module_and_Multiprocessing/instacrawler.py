import os
import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys

import requests
import re
import json
import emoji
from bs4 import BeautifulSoup

def save_list_csv(mylist, tag_name):
    file_name = tag_name + '_tag_link.csv'
    with open(file_name, "w") as file:
        for line in mylist:
            file.write(line + ',\n')

def read_csv_list(my_list, my_tag):
    tag_name = my_tag
    file_name = tag_name + '_tag_link.csv'
    
    with open(file_name) as file:
        for line in file:
            read_data = line
            my_list.append(read_data[:-2])
        file.close()
    print('load ', len(my_list), 'data from csv to list')
    
def crawling_links(my_tag, num_of_crawling_pages):
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')

    driver = Chrome(options = options)
    driver.implicitly_wait(1)

    base_url = "https://www.instagram.com/explore/tags/"
    url = base_url + my_tag

    driver.get(url)
    elem = driver.find_element_by_tag_name('body')
    link_list = []

    pagedowns = 0
    while pagedowns < num_of_crawling_pages:

        time.sleep(0.5)
        links = driver.find_elements_by_css_selector('div.v1Nh3 > a')
        for i in links:
            link_list.append(i.get_attribute('href'))

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

    driver.quit()
    
    save_list_csv(set_link_list, my_tag)
    

def data2json(my_tag, id, username, date, location, contents, hashtags, final_image_link, likes_num, comments_num):
    single_data = {
        "find_tag" : my_tag,
        "id" : id,
        "username" : username,
        "date" : date,
        "location" : location,
        "contents" : contents,
        "hashtags" : hashtags,
        "imagelinks" : final_image_link,
        "likes" : likes_num,
        "comments" : comments_num
    }
    return single_data

def save_json_file(my_tag, myjson):
    file_name = my_tag + '_rawdata.json'
    with open(file_name, 'w') as file:
        json.dump(myjson, file)
            
def crawling_rawdata(my_tag):
    my_links = []
    read_csv_list(my_links, my_tag)

    json_list = []
    emoji_keys = emoji.UNICODE_EMOJI.keys()
    
    for i in range(len(my_links)-1):
        url = my_links[i]
        req = requests.get(url)
        html = req.text
        header = req.headers
        status = req.status_code
        soup = BeautifulSoup(html, 'html.parser')

        script_contents = soup.find_all('script')
        
        ## id
        id_p = re.compile("\/p\/(.*?)\/")
        id = id_p.findall(url)[0]
        
        ## username
        user_content = soup.find(rel = "canonical")
        if not user_content:
            username = ''
        else:
            username_href = user_content.get('href')
            username_p = re.compile("instagram.com/(.*)/p")
            username = username_p.findall(str(username_href))
            if len(username) != 0:
                username = username[0]
            else:
                username = ''

        ## date
        date_p = re.compile("uploadDate\":\"(.{19})\"")
        date = date_p.findall(str(script_contents))
        if len(date) != 0:
            date = date[0]
        else:
            date = ''
        
        ## contents  
        contents_p = re.compile("\"caption\":\"(.*?)\"")
        contents = contents_p.findall(str(script_contents))

        if len(contents) > 0:
            contents = contents[0]
            contents = contents.encode('utf-8')
            contents = contents.decode('unicode_escape')
            contents = contents.encode('utf-8','ignore')
            contents = contents.decode('utf-8')
        else:
            contents = ''
        
        ## location
        location_p = re.compile("location\":.*?\"name\":\"(.*?)\"")
        location = location_p.findall(str(script_contents))
        location = ''

#         if(len(location) > 0):
#             location = location[0].encode('utf-8').decode('unicode_escape')
#         else:
#             location = ''
        
        ## hashtags
        meta_content = soup.find_all(property = "instapp:hashtags")
        hashtags = []    
        if meta_content:
            hash_tags_p = re.compile("content=\"(.*?)\"")
            emoji_hashtag = hash_tags_p.findall(str(meta_content))
            
            for tag in emoji_hashtag:
                for e in emoji_keys:
                    emoji_have = tag.find(e)
                    if emoji_have > -1:
                        tag = tag.replace(e, '')
                hashtags.append(tag)
            hashtags = list(filter(None, hashtags))

        ## remove hashtag from contents
        for tag in hashtags:
            tag = '#' + tag
            contents = contents.replace(tag, '', 1)
        
        ## preprocessing of contents
        contents = contents.replace('#','')
        contents = re.sub("\\\\u[0-9A-Fa-f]{4}", "", contents)
        contents = re.sub("[-()\"#/@;:<>{}`+=~|.!?,]", "", contents)
        contents = re.sub('\n', '', contents)
        contents = re.sub('\s+', ' ', contents)

        ## image links
        image_links_p = re.compile("\"display_resources\":\[.*?\]")
        image_links = image_links_p.findall(str(script_contents))
        
        final_image_link = []
        single_image_link_p = re.compile("\"src\":\"(.*?)\"")
        for dif_img in image_links:
            link = single_image_link_p.findall(str(dif_img))[2]
            final_image_link.append(link)
            
        if len(final_image_link) != 1:
            final_image_link = final_image_link[1:]   
            
        
        ## likes num
        likes_num_p = re.compile("\"description\":\"(.*?)Likes")
        likes_num = likes_num_p.findall(str(script_contents))

        if len(likes_num) > 0:
            likes_num = likes_num[0]
            likes_num = re.sub('[,\s]', '', likes_num)
        else:
            likes_num = '0'
        
        ## comments num
        comments_num_p = re.compile("\"description\":\".*?,(.*?)Comments")
        comments_num = comments_num_p.findall(str(script_contents))

        if len(comments_num) > 0:
            comments_num = comments_num[0]
            comments_num = re.sub('[,\s]', '', comments_num)
        else:
            comments_num = '0'
        
        ## save data as json
        single_json = data2json(my_tag, id, username, date, location, contents,
                                hashtags, final_image_link, likes_num, comments_num)
        json_list.append(single_json)
        time.sleep(1)
        if i % 30 == 0:
            print(i, '번째 데이터')
            print(single_json)
            print('------------------')
                
    save_json_file(my_tag, json_list)
    print('Crawling 완료!')
    
