from flask import Flask,request,jsonify
app = Flask(__name__)

import requests,json

@app.route("/newstopword",methods = ["GET"])
def newstopword():
    params1 = dict(request.args)

    # 官網 https://trends.google.com/trends/trendingsearches/daily?geo=TW
    # Google熱搜關鍵字，預設會取得最近兩天的關鍵字
    url = 'https://trends.google.com/trends/api/dailytrends'
    html = requests.get(url,params=params1)
    html.encoding='utf-8'

    _,datas=html.text.split(',',1)
    jsondata=json.loads(datas) #將下載資料轉換為字典

    trendingSearchesDays=jsondata['default']['trendingSearchesDays']   
 
    newsdata_list = []
    for trendingSearchesDay in trendingSearchesDays:
        # 處理日期
        newsdata_dict = {}
        news=""
        formattedDate=trendingSearchesDay['formattedDate']
        newsdata_dict['日期'] = formattedDate
        news += '日期:' + formattedDate + '\n\n'
        newsdata_dict["news"] = []

        for data in trendingSearchesDay['trendingSearches']:
            # 處理關鍵字
            data_dict = {"主題關鍵字":data['title']['query'],"關鍵字新聞":[]}  
            news += '【主題關鍵字:' + data['title']['query'] + '】' + '\n\n'

            for content in data['articles']:
                content_dict = {}
                #處理新聞詳細資訊
                content_dict["標題"] = content['title']
                content_dict["媒體"] = content['source']
                content_dict["發佈時間"] = content['timeAgo']
                content_dict["內容"] = content['snippet']
                content_dict["相關連結"] = content['url']
                data_dict["關鍵字新聞"].append(content_dict)
                news += '標題:' + content['title'] + '\n'
                news += '媒體:' + content['source'] + '\n'
                news += '發佈時間:' + content['timeAgo'] + '\n'
                news += '內容:' + content['snippet'] + '\n'
                news += '相關連結:' + content['url'] + '\n\n' 

            # 將資料寫入dict轉json匯出，以及存為txt 
            newsdata_dict["news"].append(data_dict)
        filename= trendingSearchesDay['date'] + '.txt'                 
        with open(filename,'w',encoding='utf-8') as f:
            f.write(news)
        print(filename + " 已存檔!") 
        print()
        print('-'*50)
        newsdata_list.append(newsdata_dict)
    return jsonify(newsdata_list)

if __name__ == '__main__':
    app.run(debug=True)