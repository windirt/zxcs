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
import argparse
import sqlite3
from sqlite3 import Error
import chardet

download_url = "http://www.zxcs.me/download.php?id="
book_url = "http://www.zxcs.me/post/"

title_string = ""
author_string = ""





def downloader(url, path):
    start = time.time()
    size = 0
    response = requests.get(url, stream=True)
    chunk_size = 1024
    content_size = int(response.headers['content-length'])
    if response.status_code == 200:
        print('[文件名称]:%s' % path)
        print('[文件大小]:%0.2f MB' % (content_size / chunk_size / 1024))
        with open(path, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                print('\r'+'[下载进度]:%s%.2f%%' % ('>'*int(size*50 /
                                                        content_size), float(size / content_size * 100)), end='')
    end = time.time()
    print('\n' + "[下载状态]:%s下载完成！用时%.2f秒" % (path, (end-start)))
    print('------------------------------')


def rename_file(path):
    file_type = filetype.guess(path)
    rename(path, path + '.' + file_type.extension)


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




# def get_file_name(dl_url):
#     html = get_one_page(dl_url)
#     soup = BeautifulSoup(html, 'lxml')
#     path = soup.h2.string
#     title_string = re.search(r'(?<=《)[^》]+',path)[0]
#     author_string = re.search(r'(?<=作者：).*',path)[0]
#     return path


def download_book(dl_url):
    html = get_one_page(dl_url)
    soup = BeautifulSoup(html, 'lxml')
    path = soup.h2.string + '.rar'
    url = soup.find("a", string="线路一").get("href")
    downloader(url=url, path=path)


def download_pic(pic_url):
    #global filename
    html = get_one_page(pic_url)
    soup = BeautifulSoup(html, 'lxml')
    path = soup.h1.string + '.jpg'
    try:
        url = soup.find("img", title="点击查看原图").get("src")
    except:
        url = soup.find("img", alt="（精校对版全本）").get("src")
    downloader(url=url, path=path)
    return soup.h1.string



conn = sqlite3.connect(r'library.db')
c = conn.cursor()
c.execute('SELECT * from book')
results = c.fetchall()

for result in results:
    if result[3] == 1:
        continue
    print("开始下载封面图片.....")
    filename = download_pic(book_url+result[0])
    print("开始下载书籍压缩文件.....")
    download_book(download_url+result[0])
    rarname = filename + ".rar"
    jpgname = filename + ".jpg"
    txtname = filename + ".txt"
    epubname = result[1] + "-" + result[2] + ".epub"
    print("正在解压缩文件到当前目录......")
    patoolib.extract_archive(rarname, outdir="./")
    print("开始文件转码.......")
    
    try:
        f = open(txtname, 'r', encoding="utf-16-le")
        content = f.read()
    except:
        f = open(txtname, 'r', encoding="gb18030",errors='ignore')
        content = f.read()
    


    f.close()
    f = open(txtname, 'w', encoding="utf-8")
    f.write(content)
    f.close()


    f = open(txtname,'r', encoding="utf-8")
    content = f.read()
    f.close()


    lines = content.split("\n") 
    new_content = []
    new_content.append("% "+ result[1])
    new_content.append("% "+ result[2])
    for line in lines:
        if line == "更多精校小说尽在知轩藏书下载：http://www.zxcs.me/" or line == "==========================================================" or line == result[1] or line == result[1] + " 作者：" + result[2] or line == "作者：" + result[2]:
            continue
        
        if line == "内容简介：":
            new_content.append("# " + line + "\n")
            continue
        if re.match(r'^\s*[第卷][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷].*',line):
            new_content.append("# " + line + "\n")
            continue
        line = line.replace("　　","")
        new_content.append(line + "\n")
    new_content = "\n".join(new_content)

    f = open(txtname,'w',encoding="utf=8")
    f.write(new_content)
    f.close
        

    print("开始转换EPUB文件........")
    os.system('pandoc "%s" -o "%s" -t epub3 --css=epub.css --epub-cover-image="%s"' % (txtname, epubname, jpgname))
    #print("开始转换KEPUB文件.........")
    #os.system('kepubify -i "%s"' % (epubname))
    print("删除残留文件......")
    os.system("rm %s" % (txtname))
    os.system("rm %s" % (jpgname))
    os.system("rm %s" % (rarname))
    #os.system("mv *.kepub.epub ./kepub/")
    os.system("mv *.epub ./epub/")
    c.execute('''UPDATE book SET downloaded = ? WHERE title = ?''',(1,result[1]))
    conn.commit()
    print("完成，收工，撒花！！🎉🎉")

conn.close
