# XDT
这是一个学习python，不断添加或优化功能的的工程。

## 当前版本功能
2019-09-04
1、支持从黄易天地网站下载所有小说；  
2、支持半自动从微信公众号批量下载历史文章；

## 环境要求
python3.7  
wkhtmltopdf.exe  

## 使用方法
目前功能还没有集成，单独运行不同的py程序文件，实现不同的功能。  
1、黄易天地小说下载  
    python XDT/textD/hytd.py  

    具体实现逻辑和使用方法见:  
    https://blog.csdn.net/MissYourKiss/article/details/100113661  

2、微信公众号历史文章批量下载  
    修改conf/wechat.cfg  
    下载html文件  
    python XDT/textD/wechat.py html  
    转换成pdf  
    python XDT/textD/wechat.py pdf  

    具体实现逻辑和使用方法见:
    https://blog.csdn.net/MissYourKiss/article/details/100254510