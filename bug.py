import requests
import time
import os
from bs4 import BeautifulSoup
from os import rename
import filetype
import patoolib
import re
import fileinput
import sys
import sqlite3
from sqlite3 import Error





sort_url = "http://www.zxcs.me/sort/"


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


result = input("请输入书籍分类编号: ")

dl_url = (sort_url+result)



def get_page_list(dl_url):
    html = get_one_page(dl_url)
    soup = BeautifulSoup(html, 'lxml')
    lastpage_string = soup.find("a",title="尾页").get("href")
    lastpage = re.search(r'(?<=page/).*',lastpage_string)[0]
    pages = []
    for i in range(int(lastpage)):
        pages.append(str(i+1))
        i = i + 1
    # title_string = re.search(r'(?<=《)[^》]+',path)[0]
    # author_string = re.search(r'(?<=作者：).*',path)[0]
    return ["1","2","3","4"]

pages = (get_page_list(dl_url))

def get_page_detail(index):
    details = []
    html = get_one_page(dl_url+"/page/"+index)
    print("正在处理第%s页...."% index)
    soup = BeautifulSoup(html, 'lxml')
    for dt in soup.find_all("dt"):
        a = dt.find("a")
        id = re.search(r'(?<=http://www.zxcs.me/post/).*',a.get("href"))[0]
        title = re.search(r'(?<=《)[^》]+',a.get_text())[0]
        author = re.search(r'(?<=作者：).*',a.get_text())[0]
        details.append([id,title,author])          
    return details


conn = sqlite3.connect(r"library.db")
c = conn.cursor()
for page in get_page_list(dl_url):
    for page_detail in get_page_detail(page):
        c.execute('INSERT INTO book VALUES(?,?,?,?)',(page_detail[0],page_detail[1],page_detail[2],0))

conn.commit()
conn.close()




# def download_book(dl_url):
#     global filename
#     html = get_one_page(dl_url)
#     soup = BeautifulSoup(html, 'lxml')
#     path = filename + '.rar'
#     url = soup.find("a", string="线路一").get("href")
#     downloader(url=url, path=path)






