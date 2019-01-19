from preProcessing import *

def computeTFIDF_R(tfBow, idfs, rnr):
    tfidf_R = {}
    for word, val in tfBow.items():
        tfidf_R[word] = val * idfs[word] * rnr[word]
    return tfidf_R


# 긴 토큰에게 각 단어의 TIR 값의 평균을 부여
def computeTFIDF_R_long(tfidf_R, tokens_2, length=1):
    tfidf_R_L = {}
    for token in tokens_2:  # 토큰 뭉텅이
        val = 0
        for t in token.split():  # 한 단어
            val += tfidf_R[t]
        val = float(val) / length
        tfidf_R_L[token] = val
    return tfidf_R_L


# =========================================================================================
#불러오기 >>
bow = json.loads(Path('/home/jovyan/work/분석/bow.json').read_text(), encoding='utf-8')
rnrDict = json.loads(Path('/home/jovyan/work/분석/relNonRel.json').read_text(), encoding='utf-8')
tfDict = json.loads(Path('/home/jovyan/work/분석/TFs.json').read_text(), encoding='utf-8')
idf = json.loads(Path('/home/jovyan/work/분석/idf.json').read_text(), encoding='utf-8')

tfidfDict = {}  # {ID : tf- * idf}
tfidfDict_R = {}  # {ID : tf * idf * rNr}
tfidfDict_R_len2 = {}  # 길이 2개인 토큰의 TIR 값

counter = 0
for item in path1.iterdir():

    if (item.is_dir()):  # 안보이는 디렉토리 주의
        continue
    itemJson = json.loads(item.read_text(), encoding='utf-8')
    features = itemJson["features"]
    # ==================================
    allStr = ""
    for feature in features:
        allStr = allStr + " " + feature + " "
    tokens_len2 = tokenize(allStr, 2)
    # ==================================
    ID = itemJson["id"]
    # -------------------------(일반 : tf * idf)------------------------
    tfidf = computeTFIDF(tfDict[ID], idf)
    tfidfDict[ID] = tfidf
    # ------------------------(시도2 : tf * idf * RNR)--------
    tfidf_R = computeTFIDF_R(tfDict[ID], idf, rnrDict)
    tfidfDict_R[ID] = tfidf_R
    # -----------------------(시도3 : 길이 2이상 토큰)----
    tfidf_R_L = computeTFIDF_R_long(tfidf_R, tokens_len2, 2)
    tfidfDict_R_len2[ID] = tfidf_R_L
    # -----------------------(출력)-----------------------------------------
    print("ID = ", ID, "======================")
    print("<features>")
    print(features)
    print(" < TF x IDF > ")
    displayTupList(sortDict(tfidf), 5)
    print(" < TF X IDF X RNR >")
    displayTupList(sortDict(tfidf_R), 5)  # ,True)

    print(" <TF X IDF X RNR _ 길이 2 이상 토큰>")
    displayTupList(sortDict(tfidf_R_L), 5)  # ,True)

    counter += 1
    if counter == 5:
        break