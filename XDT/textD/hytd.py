# _*_ coding:utf-8 _*_
import requests
import re
import os
import html
from functools import partial
from multiprocessing.dummy import Pool

def get_html(url):
    return requests.get(url).content.decode('utf-8')

def get_book_urls(idx_url):
    r_html = get_html(idx_url)
    book_list = re.findall("<h2>黄易小说全集</h2>.*?<ul>(.*?)</ul>",str(r_html),re.S)
    book_url_list = re.findall("<a href=\"(.*?)\">(.*?)</a>",book_list[0],re.S)
    for book_url in book_url_list:
        book_name = book_url[1]
        book_url = book_url[0]
        get_book(idx_url,book_name,book_url[1:])

def get_book(idx_url,book_name,a_book_url):
    book_path = os.path.join("..","output","novel",book_name)
    os.makedirs(book_path,exist_ok=True)
    book_url = idx_url+a_book_url
    r_html = get_html(book_url)
    cpt_list = re.findall("正文</dt>(.*?)</dl>",str(r_html),re.S)
    cpt_url_list = re.findall("href=\"(.*?)\">(.*?)</a>",cpt_list[0],re.S)

    '''
    # 改成多线程
    i=0
    for cpt_url in cpt_url_list:
        cpt_name = cpt_url[1].replace(' ','_')
        cpt_url = idx_url + cpt_url[0][1:]
        # 测试用
        if i==0:
            down_cpt(book_path,cpt_name,cpt_url)
        i=i+1
    '''
    pool = Pool(9)  #定义9个线程
    pool.map(partial(down_cpt_mult,idx_url=idx_url,book_name=book_path),cpt_url_list) #给线程传递参数
    print("【{}】下载完毕".format(book_name))

def down_cpt_mult(cpt_url,idx_url,book_name):
    cpt_name = cpt_url[1].replace(' ','_')
    cpt_url = idx_url + cpt_url[0][1:]
    down_cpt(book_name,cpt_name,cpt_url)

def down_cpt(book_name,cpt_name,cpt_url):
    # 去掉非法字符 否则会报错
    n_cpt_name = re.sub(r'[\\/:*?"<>|\r\n]+',"",cpt_name)
    path = os.path.join(book_name,n_cpt_name+'.txt')

    # 续传 如果存在就直接返回
    if os.path.exists(path):
        return
    r_html = get_html(cpt_url)
    cpt_content_html = html.unescape(r_html)
    cpt_content = re.findall("<div id=\"content\".*?</p>(.*?)<div align=\"center\">",str(cpt_content_html),re.S)
    with open(path,'w',encoding='utf-8') as f:
        f.write(cpt_content[0].replace('<br/>','\n'))



hytd_idx_url = 'https://www.hytd.com/'
get_book_urls(hytd_idx_url)