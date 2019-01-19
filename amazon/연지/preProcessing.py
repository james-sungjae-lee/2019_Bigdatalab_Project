#전처리 작업을 위한 함수들과 라이브러리를 모듈화 했습니다.
#1. amzTextAnalyze.py는 이 모듈을 import하여 여러가지(bow,tfidf,rnr)를 연산후 저장합니다.
#2. showResult.py는 저장한 값들을 이용하여, 텍스트에서 중요 키워드를 추출하여 보여줍니다.

import json
from pathlib import Path  # Path클래스 임포트
import re  # 특수문자 제거
from functools import cmp_to_key
import nltk
from nltk.corpus import wordnet
from stop_words import get_stop_words  # stop word 제거

lmtzr = nltk.WordNetLemmatizer().lemmatize
en_stop = get_stop_words('en')

# 내림차순 정렬을 위한 함수객체들
def cmp(l, r):
    if l > r:
        return 1
    elif l == r:
        return 0
    else:
        return -1


def key_func(l, r):
    if l[1] == r[1]:
        return cmp(l[0], r[0])
    return -cmp(l[1], r[1])


# dict()
# dictionary => 내림차순 정렬된 list of tuple으로 만들어서 리턴
def sortDict(bow):
    word_list = []  # 리스트에 (단어, 횟수) 꼴의 튜플을 넣을 것

    for i, k in bow.items():
        word_list.append((i, k))
    word_list.sort(key=lambda x: x[1], reverse=True)  # 횟수를 기준으로 내림차순 정렬
    word_list.sort(key=cmp_to_key(key_func))  # 횟수는같을때, 단어를 기준으로 정렬
    return word_list


# list of tuple을 출력
def displayTupList(tupList, num, withVal=False):  # 디폴트는 내림차순, 값 없이..
    counter = 0
    for tup in tupList:
        if counter == num or tup[1] < 0:
            break
        else:
            if withVal:
                print(tup[0], " : ", tup[1], "  ", end="")
            else:
                print(tup[0], "   ", end="")
            counter += 1
    print()


# 어떤 특수기호를 제거할지
def delSymbol(feature):
    str = re.sub('[^A-Za-z0-9-]+', ' ', feature)  # 알파벳, 숫자, '-'  빼고 지우기
    str = re.sub('[0-9]+', 'ㅠ', str)  # 숫자를 포함한 단어 전체를 지우기 위함.
    while (str.find("--") != -1):  # ' - ' 두개이상은 지움
        str = str.replace("--", " ")
    return str.strip('-')  # 겉에남은 '-' 제거


# 버릴단어
def isSemantic(word):
    if word == '' or word == '-' or word.find("ㅠ") != -1:  # or word == '%' or word.isdigit()
        return False
    else:
        return True


# 역시...오픈소스가 짱이야...=====================
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def normalize_text(text):
    word_pos = nltk.pos_tag(nltk.word_tokenize(text))
    lemm_words = [lmtzr(sw[0], get_wordnet_pos(sw[1])) for sw in word_pos]
    return [x.lower() for x in lemm_words][0]  # ==


# =========================================

# 입력된 길이로 토큰화 되도록 수정..
def tokenize(feature, length=1):
    tokens = []
    feature = delSymbol(feature)
    for token in feature.split():
        token = token.lower().strip('-')
        if isSemantic(token):
            tokens.append(token)
    tokens = [i for i in tokens if not i in en_stop]  ###stop words 제거
    # tokens = [lemmatizer.lemmatize(i) for i in tokens] ###표제어 추출
    tokens = [normalize_text(i) for i in tokens]  ###조금더 정교한 표제어 추출..

    # 길이 2 이상의 단어로 tokenize=====================
    returnTokens = []
    index = 0;
    leng = length;
    for i in range(len(tokens) - leng + 1):
        token = ""
        for j in range(leng):
            token = token + " " + tokens[index + j]
        index += 1
        returnTokens.append(token.strip())
    # ============================================
    return returnTokens


# 경로에 있는 모든 id.json 파일의 features로 bag of word(딕셔너리)를 만들어 리턴
def makeBow(path):
    for item in path.iterdir():
        if (item.is_dir()):  # 안보이는 디렉토리가 있다.. 주의
            continue
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]
        allStr = ""
        for feature in features:
            allStr = allStr + " " + feature + " "
        tokens = tokenize(allStr)
        for token in tokens:
            if token in bow:
                bow[token] += 1
            else:
                bow[token] = 1
    return bow


# 특정 문서(features)하나 만의 bag of word를 만들고, 단어개수 리턴.
def makeSmallBow(features):
    smallBow = {}
    counter = 0  # 단어개수
    allStr = ""
    # <tokenize 호출>==================
    for feature in features:
        allStr = allStr + " " + feature + " "
    tokens = tokenize(allStr)
    # ==============================
    for token in tokens:
        counter += 1
        if token in smallBow:
            smallBow[token] += 1
        else:
            smallBow[token] = 1
    return smallBow, counter


# 문서 하나의 tf를 계산 (dictionary)
def computeTF(features):
    smallBow, numOfWord = makeSmallBow(features)  # eachBow : 특정 상품의 word count dict
    # numOfWord : 특정 상품의 word 개수
    tf = {}  # 단어별 tf를 계산해서 넣음
    for word, count in smallBow.items():
        if (numOfWord == 0):  # feature 없는 상품..
            break
        # tf 어떻게 할까 ====================================================
        # tf[word] = count / float(numOfWord)
        # tf[word] = float(numOfWord) / count #역수 (문서 내 자주 등장한 단어는 중요하지 않다)
        tf[word] = 1  # 단어가 있냐 없냐만 따짐
        # ===============================================================
    return tf


# path 에 있는 모든 id.json 파일을 가지고, tf를 구하여 "ID" : tf   꼴의 딕셔너리 리턴
# path 여러개로 재정의
def computeAllTF(paths):
    tfDict = {}
    for path in paths:
        for item in path.iterdir():
            if (item.is_dir()):  # 안보이는 디렉토리가 있다.. 주의 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
                continue
            itemJson = json.loads(item.read_text(), encoding='utf-8')
            features = itemJson["features"]
            ID = itemJson["id"]
            tf = computeTF(features)
            tfDict[ID] = tf
    return tfDict


# 모든 tf  가지고, idf 를 계산 (dictionary)
def computeIDF(tfs):
    import math
    idf = {}
    N = len(tfs)  # 모든 상품 개수
    for ID, tf in tfs.items():
        for word, val in tf.items():
            if val > 0:
                if word in idf:
                    idf[word] += 1  # 일단은 "word : word를 가진 상품개수" 꼴의 사전 완성..
                else:
                    idf[word] = 1
    for word, val in idf.items():
        idf[word] = math.log10(N / float(val))
    return idf


# 문서 하나의 tf-idf 계산 (dictionary)
def computeTFIDF(tf, idfs):
    tfidf = {}
    for word, val in tf.items():
        tfidf[word] = val * idfs[word]
    return tfidf


# (시도1) : tf / idf
def computeTFIDF2(tf, idfs):
    tfidf2 = {}
    for word, val in tf.items():
        tfidf2[word] = val / idfs[word]
    return tfidf2

#분석할 문서들이 위치한 경로
path1 = Path('/home/jovyan/work/크롤링/relFeatures')
path2 = Path('/home/jovyan/work/크롤링/nonRelFeatures')
paths = [path1, path2]