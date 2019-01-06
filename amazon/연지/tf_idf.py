from bagOfWord import * #주피터에선 지워!

#bagOfword.json 파일이 이미 만들어져 있다고 가정! ----(bagOfWord.py 로 생성)
# 특정 문서(features)하나 만의 bag of word를 만들고, 단어개수 리턴.
def makeSmallBow(features):
    smallBow = {}
    for word, count in bow.items():
        smallBow[word] = 0
    counter = 0  # 단어개수
    for feature in features:
        feature = delSymbol(feature)  # 1. 특수기호, 이모티콘을 띄어쓰기로 대체
        for word in feature.split():  # 2. 띄어쓰기 단위로 분리
            word = word.lower().strip('-')  # 3. 겉에 남은 -  제거!
            if not isSemantic(word):  # 4. 무의미한 word는 버림
                continue
            smallBow[word] += 1
            # print(word, "카운트 1 증가")
            counter += 1
    return smallBow, counter


# 문서 하나의 tf를 계산 (dictionary)
def computeTF(bow, features):
    smallBow, numOfWord = makeSmallBow(features)  # eachBow : 특정 상품의 word count dict
    # numOfWord : 특정 상품의 word 개수
    tf = {}  # 단어별 tf를 계산해서 넣음
    for word, count in smallBow.items():
        if (numOfWord == 0):  # feature 없는 상품..
            break
        tf[word] = count / float(numOfWord)
    return tf


# 모든 tf  가지고, idf 를 계산 (dictionary)
def computeIDF(tfs):
    import math
    idf = {}
    for word, count in bow.items():
        idf[word] = 0
    N = len(tfs)  # 모든 상품 개수
    print("N -> ", N)
    for ID, tf in tfs.items():
        for word, val in tf.items():
            if val > 0:
                idf[word] += 1  # 일단은 "word : word를 가진 상품개수" 꼴의 사전 완성..
    for word, val in idf.items():
        idf[word] = math.log10(N / float(val))
    return idf


# 문서 하나의 tf-idf 계산 (dictionary)
def computeTFIDF(tfBow, idfs):
    tfidf = {}
    for word, val in tfBow.items():
        tfidf[word] = val * idfs[word]
    return tfidf


# path 에 있는 모든 id.json 파일을 가지고, tf를 구하여 "ID" : tf   꼴의 딕셔너리 리턴
def computeAllTF(path):
    count = 0
    for item in path.iterdir():
        if (item.is_dir()):  # 안보이는 디렉토리가 있다.. 주의 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
            continue
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]
        ID = itemJson["id"]

        tf = computeTF(bow, features)
        tfDict[ID] = tf
    return tfDict

if __name__ == "__main__":
    #주피터 에선 ----메인---- 이전은 삭제하고 실행(중복된 내용)
    path = Path("/home/user/ML/2_2project/featureContainer")
    bowFile = Path('/home/user/ML/2_2project/bagOfWord.json')
    bowText = bowFile.read_text(encoding = 'utf-8')
    bow = json.loads(bowText)
    emptyBow = {}
    for word, count in bow.items():
        emptyBow[word] = 0
    # ---------------메인1(tf 전부 계산)---------------
    tfDict = {} #tf 들을 저장
    tfDict = computeAllTF(path)
    # ______메인2(idf 계산)___________
    idf = computeIDF(tfDict)
    #displayTupList(sortDict(idf), -1, withVal=True)
    json.dump(idf, open(f'/home/jovyan/work/분석/idf' + '.json', 'w+'))

    #----------------메인3(tf - idf 전부 계산)-------------
    index = 0
    tfidfDict = {} #  {ID : tf-idf}
    for item in path.iterdir():
        if(item.is_dir()): #안보이는 디렉토리가 있다.. 주의 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
            continue
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]
        ID = itemJson["id"]
        tfidf = computeTFIDF(tfDict[ID], idf)
        tfidfDict[ID] = tfidf
        if index == 10:
            break
        print("<features>")
        print(features)
        print("< TF >")
        displayTupList(sortDict(tfDict[ID]), -1)
        print(" <TF - IDF > ")
        displayTupList(sortDict(tfidf), -1)
        #print(tfidf)
        index += 1
        if index == 5:
            break
    json.dump(tfidfDict, open(f'/home/jovyan/work/분석/TF-IDFs' + '.json', 'w+'))