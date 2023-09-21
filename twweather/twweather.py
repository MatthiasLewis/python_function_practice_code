from flask import Flask
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

@app.route('/<town>')
def index(town):
    # 檢查是否有鄉鎮市區代碼檔
    if not os.path.isfile('district.csv'):
        df = pd.read_excel('712693030RPKUP4RX.xlsx', header=3)
        df.drop(columns=['縣市代碼', '村里代碼', '村里名稱', '村里代碼', '村里代碼.1'], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)
        df.to_csv('district.csv', encoding='big5', index=False)

    dftown = pd.read_csv('district.csv', encoding='big5')  #區鄉鎮名稱代碼資料
    dfs = dftown[(dftown['縣市名稱']==town[:3]) & (dftown['區鄉鎮名稱']==town[3:])]

    if len(dfs) > 0:  #區鄉鎮名稱存在
        town_no = str(dfs.iloc[0,1])
        url = 'https://www.cwb.gov.tw/V8/C/W/Town/MOD/3hr/' + town_no + '_3hr_PC.html'  #三日預報網頁
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')
        soup_data = {"時間":[],"日期":[],"天氣狀況":[],'溫度(℃)':[],'溫度(℉)':[],"體感溫度(℃)":[],"體感溫度(℉)":[]\
                 ,"降雨機率":[],"相對溼度":[],"蒲福風級":[],"風速(m/s)":[],"風向":[],"舒適度":[]}
        
        # 整理日期時間欄
        for t in soup.find('tr',class_="time").find_all("span"):
            soup_data["時間"].append(t.text)
        for d in soup.find('tr').find_all("th", headers="PC3_D"):
            if d.get("id") == "PC3_D4" : soup_data["日期"] += [d.text]
            else : soup_data["日期"] += [d.text]*8
        # 整理天氣示意圖欄
        for img in soup.find_all('tr')[2].find_all("img"):
            soup_data["天氣狀況"].append(img.get("title"))
        # 整理溫度欄
        for c in soup.find_all("tr")[3].find_all("span"):
            if c.get("class")[0] == "tem-C" : soup_data['溫度(℃)'].append(c.text)
            else : soup_data['溫度(℉)'].append(c.text)
        # 整理體感溫度欄
        for f in soup.find_all("tr")[4].find_all("span"):
            if f.get("class")[0] == "tem-C" : soup_data['體感溫度(℃)'].append(f.text)
            else : soup_data['體感溫度(℉)'].append(f.text)
        # 整理降雨機率欄
        for t in soup.find_all("tr")[5].find_all("td"):
            if t.get("headers")[2] == "PC3_D4H00" : soup_data['降雨機率'] += [t.text]
            else : soup_data['降雨機率'] += [t.text]*2
        # 整理相對溼度欄
        for t in soup.find_all("tr")[6].find_all("td"):
            soup_data['相對溼度'].append(t.text)   
        # 整理蒲福風級 
        for w1 in soup.find_all("tr")[7].find_all("td"):
            soup_data['蒲福風級'].append(t.text)
        # 整理風速
        for s in soup.find_all("tr")[8].find_all("td"):
            soup_data['風速(m/s)'].append(s.text)
        # 整理風向
        for s in soup.find_all("tr")[9].find_all("td"):
            soup_data['風向'].append(s.text)
        # 整理舒適度
        for s in soup.find_all("tr")[10].find_all("td"):
            soup_data['舒適度'].append(s.text)

        # pandas讀取表格
        df = pd.DataFrame(soup_data)
        # 將日期拆分成日期、星期二欄
        df["星期"] = df['日期'].str.partition("星期")[1] + df['日期'].str.partition("星期")[2]
        df["日期"] = df['日期'].str.partition("星期")[0]
        
        # 轉為json回傳
        return df.to_json(orient='records', force_ascii=False)

    else:
        return '無此鄉鎮市區名稱！'
    
if __name__ == '__main__':
    app.run()
