from bagOfWord import * #주피터에선 지워!

#bagOfword.json 파일이 이미 만들어져 있다고 가정! ----(bagOfWord.py 로 생성)

#문서 하나의 tf를 계산 (dictionary)
def computeTF(bow, features):
    smallBow, numOfWord = makeSmallBow(features)  # eachBow : 특정 상품의 word count dict
    # numOfWord : 특정 상품의 word 개수
    tfDict = {}  # 단어별 tf를 계산해서 넣음
    for word, count in smallBow.items():
        if (numOfWord == 0):  # feature 없는 상품..
            break
        tfDict[word] = count / float(numOfWord)
    return tfDict

#모든 tf Dict를 가지고, idf 를 계산 (dictionary)
def computeIDF(dictList):
    import math
    idfDict = emptyBow
    N = len(dictList)  # 모든 상품 개수
    for dic in dictList:  # dic = tfDict 한개
        for word, val in dic.items():
            if val > 0:
                idfDict[word] += 1  # 일단은 "word : word를 가진 상품개수" 꼴의 사전 완성..
    for word, val in idfDict.items():
        idfDict[word] = math.log10(N / float(val))
    return idfDict

#문서 하나의 tf-idf 계산 (dictionary)
def computeTFIDF(tfBow, idfs):
    tfidf = {}
    for word, val in tfBow.items():
        tfidf[word] = val * idfs[word]
    return tfidf

#path 에 있는 모든 id.json 파일을 가지고, tf를 구하여 리스트에 저장.
def makeTfList(path):
    for item in path.iterdir():
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]
        ID = itemJson["id"]
        tfDict = computeTF(bow, features)
        tfDictList.append(tfDict)
    return tfDictList

if __name__ == "__main__":
    #주피터 에선 ----메인---- 이전은 삭제하고 실행(중복된 내용)
    path = Path("/home/user/ML/2_2project/featureContainer")
    bowFile = Path('/home/user/ML/2_2project/bagOfWord.json')
    bowText = bowFile.read_text(encoding = 'utf-8')
    bow = json.loads(bowText)
    emptyBow = {}
    for word, count in bow.items():
        emptyBow[word] = 0
    # ---------------메인1(tf, idf 계산하기)---------------
    tfDictList = [] #tf 들을 저장
    tfDictList = makeTfList(path)
    idfDict = computeIDF(tfDictList)
    #displayTupList(sortDict(idfDict), -1, withVal=True)

    #----------------메인2(tf - idf 계산하기)-------------
    index = 0
    tfidfDict = {} #  {ID : tf-idf}
    for item in path.iterdir():
        itemJson = json.loads(item.read_text(), encoding='utf-8')
        features = itemJson["features"]
        ID = itemJson["id"]
        tfidf = computeTFIDF(tfDictList[index], idfDict)
        tfidfDict[ID] = tfidf
        index += 1
    json.dump(tfidfDict, open(f'/home/user/ML/2_2project/TF-IDFs' + '.json', 'w+'))