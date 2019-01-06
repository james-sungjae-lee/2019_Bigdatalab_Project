import json
from pathlib import Path  # Path클래스 임포트
import re  # 특수문자 제거
from functools import cmp_to_key


#내림차순 정렬을 위한 함수객체들
def cmp(l,r):
    if l>r:
        return 1
    elif l==r :
        return 0
    else:
        return -1
def key_func(l,r):
    if l[1]==r[1]:
        return cmp(l[0],r[0])
    return -cmp(l[1],r[1])

#dictionary => 내림차순 정렬된 list of tuple으로 만들어서 리턴
def sortDict(bow):
    word_list=[] #리스트에 (단어, 횟수) 꼴의 튜플을 넣을 것

    for i,k in bow.items() :
        word_list.append((i,k))
    word_list.sort(key=lambda x:x[1], reverse=True) #횟수를 기준으로 내림차순 정렬
    word_list.sort(key=cmp_to_key(key_func))# 횟수는같을때, 단어를 기준으로 정렬
    return word_list
#list of tuple을 출력
def displayTupList(tupList, num, withVal=False):  # 디폴트는 내림차순, 값 없이..
    counter = 0
    for tup in tupList:
        if tup[1] == 0 or counter == num:
            break
        else:
            if withVal:
                print(tup[0], " : ", tup[1], "  ", end="")
            else:
                print(tup[0], "   ", end="")
            counter += 1
    print()
#어떤 특수기호를 제거할지?
#일단은 알파벳,숫자,--, % 빼고 대체
def delSymbol(feature):
    str = re.sub('[^A-Za-z0-9-]+', ' ', feature)  # 알파벳,숫자,-,% 빼고 다 지움. # str = re.sub('[^A-Za-z0-9-%]+', ' ', feature)
    str = re.sub('[0-9]+', 'ㅠ', str)  # 숫자를 ㅠ 로 바꿈 (나중에 덩어리째로 지우기)
    while (str.find("--") != -1):  # - 가 두개이상 있는경우엔 지움
        str = str.replace("--", " ")
    return str.strip('-')  # -가 사이에 낀게 아니라 겉에남아있는경우엔 제거

#버릴단어인지?
# 일단은 -- , % 만 남거나, 숫자만 남으면 버림
def isSemantic(word):
    if word == '' or word == '-' or word == '%' or word.isdigit() or word.find("ㅠ") != -1:
        return False
    else:
        return True

#경로에 있는 모든 id.json 파일의 features로 bag of word(딕셔너리)를 만들어 리턴
def makeBow(path) :
    for item in path.iterdir():
        if(item.is_dir()): #안보이는 디렉토리가 있다.. 주의 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
            continue
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]

        for feature in features:
            feature = delSymbol(feature)  # 1. 특수기호, 이모티콘을 띄어쓰기로 대체
            for word in feature.split():  # 2. 띄어쓰기 단위로 분리
                word = word.lower().strip('-')  # 3. 겉에 남은 -  제거!
                if not isSemantic(word):  # 4. 무의미한 word는 버림
                    continue
                if word in bow:
                    bow[word] += 1
                else:
                    bow[word] = 1
    return bow


if __name__ == "__main__" :
    #bagOfWord 만들고, 저장--------------------------------------------
    path = Path('/home/jovyan/work/크롤링/featureContainer')
    bow = {}
    bow = makeBow(path)
    # 횟수를 0으로 초기화 한, dictionary 틀
    json.dump(bow, open(f'/home/jovyan/work/분석/bagOfWord' + '.json', 'w+'))