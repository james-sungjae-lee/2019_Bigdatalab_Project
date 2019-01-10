import requests
import re
import time
import json
import emoji
from bs4 import BeautifulSoup

def read_csv_list(my_list, my_tag):
    tag_name = my_tag
    file_name = tag_name + '_tag_link.csv'
    
    with open(file_name) as file:
        for line in file:
            read_data = line
            my_list.append(read_data[:-2])
        file.close()
    print('load ', len(my_list), 'data from csv to list')
        
## 찾아낸 데이터를 JSON 객체로 생성하는 함수를 정의합니다.
def data2json(my_tag, id, username, date, contents, hash_tags, final_image_link, likes_num, comments_num):
    single_data = {
        "find_tag" : my_tag,
        "id" : id,
        "username" : username,
        "date" : date,
        "contents" : contents,
        "hashtags" : hash_tags,
        "imagelinks" : final_image_link,
        "likes" : likes_num,
        "comments" : comments_num
    }
    return single_data

my_tag = input('Enter your tag :')
my_links = []
read_csv_list(my_links, my_tag)
json_list = []
emoji_keys = emoji.UNICODE_EMOJI.keys()

for i in range(len(my_links)-1):
    
    test_url = my_links[i]
    req = requests.get(test_url)
    html = req.text
    header = req.headers
    status = req.status_code
    soup = BeautifulSoup(html, 'html.parser')
    script_content = soup.find_all('script')

    ## 게시글 아이디를 링크로부터 가져와 찾아냅니다.
    id_p = re.compile("\/p\/(.*?)\/")
    id = id_p.findall(test_url)[0]

    ## 사용자 이름을 rel='canonical'에서 주소를 가져와 찾아냅니다.
    user_content = soup.find(rel="canonical")
    if user_content:
        username_pp = user_content.get('href')
        username_p = re.compile("instagram.com/(.*)/p")
        username = username_p.findall(str(username_pp))
        if len(username) > 0:
            username = username[0]


    ## 날짜를 header 파일에서 'Date' 부분을 가져와 찾아냅니다.
    date_p = re.compile("uploadDate\":\"(.{19})\"")
    date = date_p.findall(str(script_content))
    if len(date) > 0:
        date = date[0]
    else:
        date = 0
        

    ## 글 내용을 script 내용에서 caption 부분을 가져와 찾아냅니다.
    ## 태그 내용을 contents 에서 빼는 과정이 필요할지도 모릅니다.
    if script_content:   
        contents_p = re.compile("\"caption\":\"(.*?)\"")
        contents = contents_p.findall(str(script_content))
        
        if len(contents) > 0:
            contents = contents[0]
            contents = contents.encode('utf-8')
            contents = contents.decode('unicode_escape')
            contents = contents.encode('utf-8','ignore')
            contents = contents.decode('utf-8')
        else:
            contents = ""

    ## 해쉬태그를 property='instapp:hashtags' 에서 contetn= 이후 부분을 가져와 찾아냅니다.
    meta_content = soup.find_all(property = "instapp:hashtags")
    if meta_content:
        hash_tags_p = re.compile("content=\"(.*?)\"")
        emoji_hashtag = hash_tags_p.findall(str(meta_content))
        
        ## 해쉬태그에서 emoji 를 삭제하는 코드입니다.
        hash_tags = []
        for tag in emoji_hashtag:
            for e in emoji_keys:
                emoji_have = tag.find(e)

                if emoji_have > -1:
                    tag = tag.replace(e,'')
            hash_tags.append(tag)
            
        hash_tags = list(filter(None,hash_tags))      
    
        ## 해쉬태그 리스트가 완성되었으므로, 해당 해쉬태그가 본문에 작성되었다면 삭제해 줍니다.
        for tag in hash_tags:
            tag = '#' + tag
            contents = contents.replace(tag,"",1)

    ## regex 를 이용하여 텍스트 데이터 전처리
    contents = contents.replace('#','')
#     contents = re.sub("\\\\u[0-9A-Fa-f]{4}", "", contents)
    contents = re.sub("[-()\"#/@;:<>{}`+=~|.!?,]", "", contents)
    contents = re.sub('\n', '', contents)
    contents = re.sub('\s+', ' ', contents)        

    ## 이미지 링크를 display_resources 에서 가져와 찾아냅니다.
    ## 이미지가 N개일 때, 총 N+1 종류의 이미지 링크가 존재합니다.
    ## 확인해 보니 1번째와 2번째 이미지는 동일하며, 나머지는 서로 다른 이미지였습니다.
    ## 추정해 보면 1번째 이미지는 2번째 이후 이미지들을 대표하는 하나의 이미지라 할 수 있습니다.
    ## 각 이미지에 대해 서로 다른 resolution 으로 3가지의 다른 형태로 저장된 것을 볼 수 있습니다.
    ## 1번째는 640, 2번째는 750, 3번째는 원본 크기인것으로 보이며, 이 중에서 원본 크기의 링크만 저장합니다.
    image_links_p = re.compile("\"display_resources\":\[.*?\]")
    image_links = image_links_p.findall(str(script_content))

    final_image_link = []
    single_image_link_p = re.compile("\"src\":\"(.*?)\"")
    for dif_img in image_links:
        link = single_image_link_p.findall(str(dif_img))[2]
        final_image_link.append(link)
        

    ## 이미지가 1개일 때는 대표 이미지만 존재하므로, 이에 대한 예외처리가 필요하다
    if len(final_image_link) != 1:
        final_image_link = final_image_link[1:]    

    ## like_num, comment_num 을 description 에서 찾아냅니다.
    likes_num_p = re.compile("\"description\":\"(.*?)Likes")
    likes_num = likes_num_p.findall(str(script_content))
    
    if len(likes_num) > 0:
        likes_num = likes_num[0]
        likes_num = re.sub('[,\s]', '', likes_num)
    else:
        likes_num = 0

    comments_num_p = re.compile("\"description\":\".*?,(.*?)Comments")
    comments_num = comments_num_p.findall(str(script_content))

    if len(comments_num) > 0:
        comments_num = comments_num[0]
        comments_num = re.sub('[,\s]', '', comments_num)
    else:
        comments_num = 0

    single_json = data2json(my_tag, id, username, date, contents, hash_tags, final_image_link, likes_num, comments_num)
    json_list.append(single_json)
    time.sleep(0.1)
    if i % 100 == 0:
        print(i, '번째 데이터')
        print(single_json)
        print('------------------')
        
## 생성한 데이터를 파일 형태로 저장합니다.

def save_jsonlist_json(myjson):
    file_name = my_tag + '_rawdata.json'
    with open(file_name, "w") as file:
        for line in myjson:
            file.write(str(line) + ',\n')

save_jsonlist_json(json_list)

