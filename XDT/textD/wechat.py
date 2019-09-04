# _*_ coding:utf-8 _*_
import os,sys
import requests
import json
import subprocess
import re
import random
import time
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from time import sleep

class ArticleInfo():
    def __init__(self,url,title,idx_num,atc_datetime): #idx_num是为了方便保存图片命名
        self.url = url
        self.title = title
        self.idx_num = idx_num
        self.atc_datetime = atc_datetime

def read_file(file_path):
    with open(file_path,"r",encoding="utf-8") as f:
        file_content = f.read()
    return file_content

def save_file(file_path,file_content):
    with open(file_path,"w",encoding="utf-8") as f:
        f.write(file_content)

def get_html(url):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1219.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4",
        'Connection':'keep-alive'
    }
    response = requests.get(url,headers = headers,proxies=None)
    if response.status_code == 200:
        htmltxt = response.text #返回的网页正文
        return htmltxt
    else:
        return None

def get_save_image(url,img_file_path):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1219.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4",
        'Connection':'keep-alive'
    }
    response = requests.get(url,headers = headers,proxies=None)
    with open(img_file_path,"wb") as f:
        f.write(response.content)

def get_article_list(json_path):
    """
    通过抓取的包的json文件，获取所有文章的信息的列表
    """
    file_list = os.listdir(json_path) #jsonpath是fiddler导出的文件夹路径
    article_list = [] # 用来保存所有文章的列表
    for file in file_list:
        file_path = os.path.join(json_path,file)
        file_cont = read_file(file_path)
        json_cont = json.loads(file_cont)
        general_msg_list = json_cont['general_msg_list']
        json_list = json.loads(general_msg_list)
        #print(json_list['list'][0]['comm_msg_info']['datetime'])
        for lst in json_list['list']:
            atc_idx = 0 # 每个时间可以发多篇文章 为了方便后续图片命名
            seconds_datetime = lst['comm_msg_info']['datetime']
            atc_datetime = seconds_to_time(seconds_datetime)
            if lst['comm_msg_info']['type'] == 49: # 49为普通的图文
                atc_idx+=1
                url = lst['app_msg_ext_info']['content_url']
                title = lst['app_msg_ext_info']['title']
                atc_info = ArticleInfo(url,title,atc_idx,atc_datetime)
                article_list.append(atc_info)
            if 1 == lst['app_msg_ext_info']['is_multi']: # 一次发多篇
                multi_app_msg_item_list = lst['app_msg_ext_info']['multi_app_msg_item_list']
                for multi in multi_app_msg_item_list:
                    atc_idx+=1
                    url = multi['content_url']
                    title = multi['title']
                    mul_act_info = ArticleInfo(url,title,atc_idx,atc_datetime)
                    article_list.append(mul_act_info)
    return article_list

def chg_img_link(bs_html):
    link_list = bs_html.findAll("link")
    for link in link_list:
        href = link.attrs["href"]
        if href.startswith("//"):
            new_href = "http:"+href
            link.attrs["href"]=new_href

def rep_image(org_html,local_img_path,html_name):
    bs_html = BeautifulSoup(org_html,"lxml")
    img_list = bs_html.findAll("img")
    img_idx = 0 # 计数和命名用
    for img in img_list:
        img_idx+=1
        org_url = "" # 图片的真实地址
        if "data-src" in img.attrs: # <img  data-src="..."
            org_url = img.attrs['data-src']
        elif "src" in img.attrs : # <img  src="..."
            org_url = img.attrs['src']
        if org_url.startswith("//"):
            org_url = "http:" + org_url
        if len(org_url) > 0 :
            print("download image ",img_idx)
            if "data-type" in img.attrs:
                img_type = img.attrs["data-type"]
            else:
                img_type = "png"
            img_name = html_name + "_" + str(img_idx) + "." +img_type
            img_file_path = os.path.join(local_img_path,img_name)
            get_save_image(org_url,img_file_path) # 下载并保存图片
            img.attrs["src"] = "images/" + img_name
        else:
            img.attrs["src"] = ""
    chg_img_link(bs_html)
    return str(bs_html)


def down_html(json_path,html_path):
    if not os.path.exists(html_path):
        os.makedirs(html_path) # 创建保存html文件的文件夹
    local_img_path = os.path.join(html_path,"images")
    if not os.path.lexists(local_img_path):
        os.makedirs(local_img_path) # 创建保存本地图片的文件夹
    article_list = get_article_list(json_path)
    article_list.sort(key=lambda x:x.atc_datetime, reverse=True) # 根据文章发表时间倒序排列
    tot_article = len(article_list) # 文章的总数量
    i = 0 #计数用
    for atc in article_list:
        i+=1
        atc_unique_name = str(atc.atc_datetime) + "_" + str(atc.idx_num) # 时间+序号 作为同一时间发表的文章的唯一标识
        html_name = atc_unique_name+".html"
        html_file_path = os.path.join(html_path,html_name)
        print(i,"of",tot_article,atc_unique_name,atc.title)
        if os.path.exists(html_file_path): # 支持续传
            print("{} existed already!".format(html_file_path))
            continue
        org_atc_html = get_html(atc.url)
        new_atc_html = rep_image(org_atc_html,local_img_path,html_name)
        save_file(html_file_path,new_atc_html)
        sleep(round(random.uniform(1,3),2))
        """for test
        if i>0 :
            break
        """

def conv_html_pdf(html_path,pdf_path):
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    f_list = os.listdir(html_path)
    for f in f_list:
        if (not f[-5:]==".html") or ("tmp" in f): #不是html文件的不转换，含有tmp的不转换
            continue
        html_file_path = os.path.join(html_path,f)
        html_tmp_file = html_file_path[:-5]+"_tmp.html" #生成临时文件，供转pdf用
        html_str = read_file(html_file_path)
        bs_html = BeautifulSoup(html_str,"lxml")
        pdf_title = ""
        title_tag = bs_html.find(id="activity-name")
        if title_tag is not None:
            pdf_title = "_"+title_tag.get_text().replace(" ", "").replace("  ","").replace("\n","")
        print(pdf_title)
        r_idx = html_file_path.rindex("/") + 1
        pdf_name = html_file_path[r_idx:-5]+pdf_title
        pdf_file_path = os.path.join(pdf_path,pdf_name+".pdf")
        """
        加快转换速度，把临时文件中的不必要的元素去掉
        """
        [s.extract() for s in bs_html(["script","iframe","link"])]
        save_file(html_tmp_file,str(bs_html))
        call_wkhtmltopdf(html_tmp_file,pdf_file_path)

def call_wkhtmltopdf(html_file_path,pdf_file_path,skipExists=True,removehtml=True):
    if skipExists and os.path.exists(pdf_file_path):
        print("pdf_file_path already existed!")
        if removehtml :
            os.remove(html_file_path)
        return
    exe_path = cfg['wkhtmltopdf'] #wkhtmltopdf.exe的保存路径
    cmd_list = []
    cmd_list.append(" --load-error-handling ignore ")
    cmd_list.append(" "+ html_file_path +" ")
    cmd_list.append(" "+ pdf_file_path +" ")
    cmd_str = exe_path + "".join(cmd_list)
    print(cmd_str)
    subprocess.check_call(cmd_str, shell=False)
    if removehtml:
        os.remove(html_file_path)

def get_config():
    cfg_file = read_file("conf/wechat.cfg")
    cfg_file = cfg_file.replace("\\\\","/").replace("\\","/") #防止json中有 / 导致无法识别
    cfg_json = json.loads(cfg_file)
    return cfg_json

def seconds_to_time(seconds):
    taime_array = time.localtime(seconds) # 1970-01-01 00:00:00 到发表时的秒数
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", taime_array)
    date_time =datetime.strptime(other_style_time, "%Y-%m-%d %H:%M:%S")
    return str(date_time).replace("-","").replace(":","").replace(" ","").replace("|","丨")


cfg = get_config() # 获得配置文件的全局变量
#get_article_list("./tmp/") # for test
#down_html("./tmp/","./html/")# for test

if __name__ == "__main__":

    if len(sys.argv) == 1:
        arg = None
    else:
        arg = sys.argv[1]
    if arg is None or arg == "html":
        down_html(cfg['jsonDir'],cfg['htmlDir'])
    elif arg == "pdf":
        conv_html_pdf(cfg['htmlDir'],cfg['pdfDir'])