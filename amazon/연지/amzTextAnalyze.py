from preProcessing import *
#미리 정의한 함수와 라이브러리를 사용하여, 분석에 필요한 값들을 모두 계산하여 저장.

# 1단계 >> bow + tfDIct + rnrCounter 한번에 생성
# (tokenize 호출한 김에 한번에 연산하기 편한 것들을 한꺼번에 계산)
def bow_tfs_rnr(paths):
    bow = {}
    rnrCounter = {}  # word : {"R": , "N": }
    tfDict = {}
    pathCounter = 0
    for path in paths:
        pathCounter += 1
        for item in path.iterdir():
            if (item.is_dir()):
                continue
            itemJson = json.loads(item.read_text(), encoding='utf-8')
            features = itemJson["features"]
            ID = itemJson["id"]
            category = itemJson["category"]
            # 카테고리 지정 (Relative or nonRelative)
            RN = None
            if category == "sweater" or category == "hoodies&sweatshirts" or category == "dress":
                RN = "R"
            elif category == "skirt" or "pants" or "nonRel":
                RN = "N"
            else:
                print("예상치 못한 카테고리 >> " + category)
                return
            # <tokenize 호출>===================================
            featureStr = ""
            for feature in features:
                featureStr = featureStr + " " + feature + " "
            tokens = tokenize(featureStr)
            # ===============================================

            # <tokens 로 bow, rnrCounter, tfDict 동시생성>=============
            tf = {}
            for token in tokens:
                if token in bow:  # bow
                    bow[token] += 1
                else:
                    bow[token] = 1
                if token not in rnrCounter:  # RNR
                    rnrCounter[token] = {"R": 0, "N": 0}
                else:
                    rnrCounter[token][RN] += 1
                if token not in tf:  # TF
                    tf[token] = 1  # tf는 0또는1의 값만 가짐
            # ===============================================
            tfDict[ID] = tf  # 원래 TF정의대로 값을 구하고 싶으면 추가 연산 필요

    return bow, rnrCounter, tfDict

if __name__ == "__main__":
    bow, rnrCounter, tfDict = bow_tfs_rnr(paths)

    rnrDict = {}
    counter = 0  # nonRelative에는 등장하지 않은 단어 수

    #rnrDict 만들기
    for token, val in rnrCounter.items():
        if val["N"] == 0:
            counter += 1
            rnrDict[token] = 586  # 이 값을 뭘로 해야할까 =====================
        else:
            rnrDict[token] = val["R"] / val["N"]
            # 1. non relative에서 한번도 안나온 단어일때.. => # 중요한 단어 또는 오타
            #       최댓값으로 설정? (586)
            # 2. 값의 범위가 너무 넓다: 0 ~ 586..
            #       로그? 혹은 normalize?
    #2단계 >> idf 계산
    idf = computeIDF(tfDict)

    #저장 >>
    json.dump(bow, open(f'/home/jovyan/work/분석/bow' + '.json', 'w+'))
    json.dump(rnrDict, open(f'/home/jovyan/work/분석/relNonRel' + '.json', 'w+'))
    json.dump(tfDict, open(f'/home/jovyan/work/분석/TFs' + '.json', 'w+'))
    json.dump(idf, open(f'/home/jovyan/work/분석/idf' + '.json', 'w+'))