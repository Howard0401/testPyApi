import requests
import time
from threading import Thread
from queue import Queue
from bs4 import BeautifulSoup
import json
import pandas
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_restful import Resource

#import pytest
#from app import app

app = Flask(__name__)
api = Api(app)
name = ''
s = ''

def run_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print('running', end-start, 's')
    return wrapper


class Spider():

    def __init__(self):
        self.qurl = Queue()
        self.data = list()
        self.page_num = 1
        self.thread_num = 1
        self.ePlatform = list()
        self.ProductName = list()
        self.ProductPrice = list()
        self.HrefValue = list()
        self.ImgValue = list()
        self.name = ""

    def produce_url(self,name):
#        request_data = request.get_data(as_text = True)
        baseurl = "https://feebee.com.tw/s/"+ name +"/?mode=l&ptab=0&page={}"
        for i in range(1, self.page_num + 1):
            url = baseurl.format(i)
            self.qurl.put(url) # 生成URL存入队列，等待其他线程提取

    def get_info(self):
        while not self.qurl.empty(): # 保证url遍历结束后能退出线程
            url = self.qurl.get() # 从队列中获取URL
            print('crawling', url)
            headers = {
                       'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  
                      }
            r = requests.get(url, headers = headers)
            soup = BeautifulSoup(r.text, 'lxml')
            seltedSoup = soup.select("div#search_result > div#search_result_container > div.bd > ol#list_view > li.items > span.items_container > a.items_link")
            selImgSoup = soup.select('div#search_result > div#search_result_container > div.bd > ol#list_view > li.items > span.img_container > a.items_link')
            for item in seltedSoup:
                self.ePlatform.append(item.get('data-store'))
                self.ProductName.append(item.get('title'))
                self.ProductPrice.append(item.get('data-price'))
                self.HrefValue.append(item.get('href'))
##                print(eComPlattform)
            for img in selImgSoup:
                self.ImgValue.append(img.select_one('img').get('data-src'))
            data = {    
            "ePlatform": self.ePlatform,
            "ProductName": self.ProductName,
            "ProductPrice":  self.ProductPrice,
            "Href": self.HrefValue,
            "Img": self.ImgValue
            }
            self.data.append(data)
    @run_time
    def run(self,name):
        self.produce_url(name)
        ths = []
        for _ in range(self.thread_num):
            th = Thread(target=self.get_info)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
        for n in self.data:
            output = n
        table = pandas.DataFrame(output)
#        print(table)
        global s
        s = table.to_json(orient='records', force_ascii=False)
        
@app.route('/press', methods=['POST'])
def test():
    data=request.get_json()
    global name     
    name=data['name']
    Spider().run(name)
    return s

@app.errorhandler(404)
def notFound(error):
    return'404'
    
if __name__ == '__main__':
    app.run(host="buildschoolprice.azurewebsites.net")