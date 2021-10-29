import requests
import pymysql
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from flask import Flask, request # request import 추가
import json


def cosine_sim(count):
    # db에서 모든 기사 count, 내용 가져오기
    db = 'NEWS1001'
    SQL = 'SELECT COUNT, TITLE, CATEGORY, COMPANY FROM ' + db + ';'
    curs.execute(SQL)
    temp = curs.fetchall()
    df = pd.DataFrame(list(temp), columns=['count', 'title', 'category', 'content'])

    # count에 해당하는 기사 카테고리 가져오기
    count_idx = (df[df['count'] == count].index.tolist())[0]
    this_category = df.loc[count_idx, 'category']

    # 같은 카테고리 기사로 추천 범위를 좁힘
    diff_category = df[df['category'] != this_category].index
    df = df.drop(diff_category)

    # 열'count'의 값이 count인 기사의 행 번호 가져오기
    df.reset_index(drop=True, inplace=True)
    count_idx2 = df.index[df['count'] == count].tolist()[0]

    # doc: 기사 본문(문서)
    # tfidf_mat: 문서들을 벡터화함
    doc = list(df['content'])
    # max_features 조정 가능
    tfidf = TfidfVectorizer(max_features=300)
    tfidf_mat = tfidf.fit_transform(doc).toarray()

    sim = cosine_similarity(tfidf_mat, tfidf_mat)

    sim_scores = list(enumerate(sim[count_idx2]))

    # 유사도가 높은 순서대로 정렬
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 상위 인덱스와 유사도 추출
    sim_scores = sim_scores[1:6]

    # 원하는 기사와 유사한 기사들의 인덱스를 구함
    news_index = [i[0] for i in sim_scores]
    result_title = df['title'].iloc[news_index]

    # df에서 기사들의 인덱스를 이용하여 count를 구함
    result_count = df['count'].iloc[news_index].tolist()

    return result_count

app = Flask (__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def root():
    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        return 'No paramete1223r4'

    parameters = ''
    result_list=[]
    for key in parameter_dict.keys():
        result_list.extend(cosine_sim(int(request.args[key])))
        print(request.args[key])
    parameters=" ".join([str(_) for _ in result_list])
    return parameters


@app.route('/update')
def root2():
    # EX) 127.0.0.1:5000/update?id=abc&newsid=4
    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        return '오류'
    a=list()
    for key in parameter_dict.keys():
        a.append(request.args[key])

    SQL='SELECT * FROM USER1 WHERE USERID="'+a[0]+'"'
    curs.execute(SQL)
    temp=curs.fetchall()
    temp=temp[0][2]

    sent=''
    temp2=list()
    for i in range(len(temp)):
        if i==len(temp)-1:
            sent += temp[i]
            temp2.append(int(sent))

        elif temp[i]==',':
            temp2.append(int(sent))
            sent=''

        else:
            sent+=temp[i]

    if int(a[1]) not in temp2:
        temp2.append(int(a[1]))
        sentence=''
        for i in range(len(temp2)):
            sentence+=str(temp2[i])+','
        sentence=sentence[0:-1]

        SQL="UPDATE USER1 SET PREFER_NEWSID='%s' WHERE USERID='%s'"%(sentence,a[0])
        curs.execute(SQL)
        conn.commit()
        return "업데이트 성공"
    else:
        return "업데이트 실패(이미 선택했던 뉴스일 수 있음)"



@app.route('/signin')
def index2():
    # EX) 127.0.0.1:5000/signin?id=abc&pw=123&news=1,2,3
    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        return 'No parameter select'

    a=list()
    for key in parameter_dict.keys():
        a.append(request.args[key])

    SQL='SELECT * FROM USER1 WHERE USERID="'+a[0]+'"'
    temp=curs.execute(SQL)

    if temp==1: # 실패
        return "이미 존재하는 아이디"
    else:
        SQL="INSERT INTO USER1(USERID,USERPW,PREFER_NEWSID) VALUES('%s','%s','%s');"%(a[0],a[1],a[2])
        curs.execute(SQL)
        conn.commit()
    return "성공"

@app.route('/init')
def asdfg():
    # EX) 127.0.0.1:5000/init

    SQL='SELECT * FROM NEWS1001'
    curs.execute(SQL)
    row_headers = [x[0] for x in curs.description]

    result = curs.fetchall()

    json_data=[]
    for i in result:
        json_data.append(dict(zip(row_headers,i)))
    return json.dumps(json_data,ensure_ascii=False)




@app.route('/login')
def asdf():
    # EX) 127.0.0.1:5000/login?id=abc&pw=123
    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        print("1")
        return 'fail'
    else:
        print(len(parameter_dict))

    a=list()
    for key in parameter_dict.keys():
        a.append(request.args[key])

    SQL='SELECT * FROM USER1 WHERE USERID="'+a[0]+'"'
    curs.execute(SQL)
    temp=curs.fetchall()

    if len(temp)==0:
        print("22")
        return "fail"

    if temp[0][0]==a[0] and temp[0][1]==a[1]:
        print("3")
        return "success"
    else:
        print("4")
        return "fail"



@app.route('/select')
def root3():

    # user1 테이블의 해당 유저 userid를 가져온다.
    # EX) 127.0.0.1:5000/select?param=abc

    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        return 'No parameter select'


    userId="default"
    for key in parameter_dict.keys():
        userId=(request.args[key])

    curs.execute('SELECT * FROM USER1 WHERE USERID="%s";'%(userId))
    selectAll=curs.fetchall()
    newsList=selectAll[0][2].replace(',',' ')
    #newsList = 1 2 3 10 11

    sent=''
    temp2=list()

    for i in newsList:
        if i!=' ':
            sent+=i
        else:
            temp2.append(int(sent))
            sent=''
    temp2.append(int(sent))

    print('userNewsList =',temp2)


    result = list()
    for i in range(-1,-len(temp2)-1,-1):
        if i==-4:
            break
        print("selectNews =",temp2[i])
        result.append(cosine_sim(int(temp2[i])))
    print('result=',result)
    print((result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[1][0], result[1][1], result[1][2],
     result[1][3], result[1][4], result[2][0], result[2][1], result[2][2], result[2][3], result[2][4]))
    #curs.execute('SELECT COUNT FROM NEWS1001 WHERE COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s" OR COUNT="%s";'% (result[0][0],result[0][1],result[0][2],result[0][3],result[0][4],result[1][0],result[1][1],result[1][2],result[1][3],result[1][4],result[2][0],result[2][1],result[2][2],result[2][3],result[2][4]) )
    #result = curs.fetchall()
    result = str(result).replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace(',', '')
    data = json.dumps(result,ensure_ascii=False)
    return data

    
if __name__ == "__main__":
    conn = pymysql.connect(host='newdb.c7p2ncpgik7h.ap-northeast-2.rds.amazonaws.com', user='admin', password='1dlckdals!',
                       db='TEST1', charset='utf8')
    curs = conn.cursor()
    session = requests.Session()
    app.run(host='0.0.0.0',port=5000)



