import requests
from bs4 import BeautifulSoup
import json,time
from flask import Flask,request,jsonify
app = Flask(__name__)

import requests,json

@app.route("/getworkdata1111",methods = ["GET"])
def work1111():
    arg = request.args
    page = int(arg["page"])

    #取得各縣市代碼對照表
    res = requests.get("https://www.1111.com.tw/includesU/tcodeMenu/data/tCodeCity.js?v=0.5882087571592514")
    aa = res.text.partition("['tCodeCity'] = ")[2].replace(";","")
    bb = json.loads(aa)
    #找到目標縣市的代碼
    for k in bb["arr"]:
        if k["v1"] != arg["v1"] or k["v"] != arg["v"]: continue
        else : county = k["k"]
    #取得要的工作類型
    worktype = arg["worktype"]

    # 1111data 最多抓10頁
    # 現在使用webdriver，要用https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json查符合版本的driver下載
    res = requests.get(f"https://www.1111.com.tw/search/job?c0={county}&col=da&ks={worktype}&page={page}&sort=desc")
    soup = BeautifulSoup(res.text,"lxml")

    workdata =  {"page_1":str(soup)}
    sumwork = int(soup.find("div",class_="job_count").get("data-count"))
    # 取得工作數量的頁數
    page_1 = sumwork//20
    if (page_1-page) > 10 : page_1 = 10+page

    for page_2 in range(page+1,page_1+1):
        res = requests.get(f"https://www.1111.com.tw/search/job?c0={county}&col=da&ks={worktype}&page={page_2}&sort=desc")
        soup = BeautifulSoup(res.text,"lxml")
        workdata.update({f"page_{page_2}":str(soup)})
        print("page",page_2)
    
    return jsonify(workdata)

if __name__ == "__main__":
    app.run(debug=True)
