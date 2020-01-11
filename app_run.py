import aiohttp
import asyncio
import pandas
import time
from flask import Flask, request
from bs4 import BeautifulSoup

headers = {
    'user-agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}
url = "https://feebee.com.tw/channel/mobile"
pName = list()
img = list()
minPrice = list()
maxPrice = list()
data = {
    "PName": pName,
    "PImg": img,
    "PMinPrice": minPrice,
    "PMaxPrice": maxPrice,
}
app = Flask(__name__)

def _init_(self, url, html):
    self.url = url 
    self.headers = headers
    self.html = html 
    self.data = ""

def _parse_results(self, url, html):
    # print(url)
    try: 
      soup = BeautifulSoup(html, 'html.parser')
      for i in range(10):
          pName.append(soup.select("div#mobile_手機 > ul > li > a.link_ghost > img")[i].get('alt'))
          # print('pName:', pName)
          img.append(soup.select("div#mobile_手機 > ul > li > a.link_ghost > img")[i].get('src'))
          # print('img:', img)

      for i in range(30):
        if(i%3 == 1):
          minPrice.append(soup.select("div#mobile_手機 > ul > li > span > meta")[i] .get('content'))
          # print('minPrice:' ,minPrice, i )
        if(i%3 == 2):
          maxPrice.append(soup.select("div#mobile_手機 > ul > li > span > meta")[i] .get('content'))
          # print('maxPrice:' ,maxPrice, i)
    except Exception as e:
      raise e

async def fetch(session, url, headers):
    async with  session.get(url, headers = headers, timeout = 10) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as client:
        html = await fetch(client, url, headers = headers)
        _parse_results(html, url, html)

loop = asyncio.get_event_loop()
t1 = time.time()
@app.route('/', methods=['POST'])
def gogo():
  t2 = time.time()
  print('t2-t1', t2-t1)
  loop.run_until_complete(main())
  t3 = time.time()
  print('t2-t1', t3-t2)
  table = pandas.DataFrame(data)
  output = table.to_json(orient='records', force_ascii=False)
  t4= time.time()
  print('t4-t3', t4-t3)
  return output


@app.route('/', methods=['GET'])
def getDisplay():
    return "Please Use Post Method"


if __name__ == '__main__':
    app.run()
