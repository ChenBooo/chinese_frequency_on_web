import re
import sys
import zmq
import time
import json
import queue
import threading
from bs4 import BeautifulSoup
from urllib.request import urlopen
from collections import defaultdict
from urllib.parse import urlparse, quote


WEB = None
OUT = set()
searched = set()
DIC = defaultdict(int)
update_lock = threading.Lock()

TRY_MAX_BEFROE_QUIT = 3
TRY_TIME_INTERVAL_S = 60
THREAD_TRY_TIME_INTERVAL_S = 5

def get_page_chinese(bsobj):
    """获取页面中所有的中文字符"""
    text = bsobj.get_text()
    words = re.findall(r"[\u4e00-\u9fa5]+", text)
    words = ''.join(words)
    return list(words)


def get_page_link(bsobj):
    """获取页面中所有链接，其中外链只保存path主机url"""
    global OUT, WEB
    
    a = bsobj.findAll("a", href=re.compile("^(http|www|/).+$"))
    all_link = [link.attrs['href'] for link in a if 'href' in link.attrs]

    out_link = set()
    iner_link = set()
    for link in all_link:
        res = urlparse(link.rstrip("/"))
        if res.netloc == WEB.netloc:
            if res.scheme == "":
                iner_link.add("http://" + link.lstrip("/"))
            else:
                iner_link.add(link.lstrip("/"))
        elif res.netloc == '':
            iner_link.add(WEB.scheme + "://" + WEB.netloc + "/" + link.lstrip("/"))
        else:
            OUT.add(res.scheme + "://" + res.netloc)

    return iner_link
        
        
def get_page_info(url):
    global DIC

    if url in searched:
        return None

    searched.add(url)

    try:
        html = urlopen(url)
    except UnicodeEncodeError:
        url = quote(url, safe='/:?=.')
        html = urlopen(url)

    bsObj = BeautifulSoup(html, "html.parser")

    words = get_page_chinese(bsObj)

    with update_lock:
        for word in words:
            DIC[word] += 1

    return get_page_link(bsObj)
    

def spider(q, id_):
    """线程执行函数，正常状态下每个线程独自爬取分类树中的一个分支，
    当分支爬取结束后，转向另一个待爬取的分支。

    输入：线程节点池，由归宿各线程的队列组成的列表
          当前线程所有的队列id
    """
    myq = q[id_]

    def get_next_url():
        global THREAD_TRY_TIME_INTERVAL_S
        
        try:
            return myq.get_nowait()
        except queue.Empty:
            time.sleep(THREAD_TRY_TIME_INTERVAL_S)
            for oq in q:
                try:
                    return oq.get_nowait()
                except queue.Empty:
                    pass
        return None

    while True:    
        url = get_next_url()
        
        if url is None:
            break

        try:
            child = get_page_info(url)
        except Exception as e:
            print(url, "get page info", e)

        if child is not None:
            for c in child:
                myq.put(c)


def start_spider(url, thread_number):
    """启动爬虫
    输入：信息保持文件名
    """
    start_time = time.time()

    threads = []
    queue_pool = []
    
    for i in range(thread_number):
        q = queue.Queue()
        queue_pool.append(q)
        
        t = threading.Thread(target=spider, kwargs={'q': queue_pool, 'id_': i})
        threads.append(t)

    queue_pool[0].put(url)

    for t in threads:
        t.setDaemon(True)
        t.start()
            
    for t in threads:
        t.join()

    print("process spend {0} seconds.".format(time.time() - start_time))

def init():
    global WEB, DIC, OUT
    global searched

    WEB = None
    DIC.clear()
    OUT.clear()
    searched.clear()
    
#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

def main():
    global WEB, DIC, OUT
    global TRY_TIME_INTERVAL_S
    global TRY_MAX_BEFROE_QUIT

    with open("cfg.json") as fp:
        config = json.load(fp)
    
    serve = config["serve"]
    thread_number = config["threads"]

    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to frequency server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + serve)

    send = {}
    try_max = TRY_MAX_BEFROE_QUIT

    while True:
        socket.send_json(send)
        message = socket.recv_json()
        print("receive message %s …" % message)
        if message.get("web_url") is None:
            time.sleep(TRY_TIME_INTERVAL_S)
            try_max -= 1
            if try_max < 0:
                print("try 3 times. still no new url. exit.")
                break
            else:
                continue
        init()
        
        web_url = message["web_url"]
        WEB = urlparse(web_url.rstrip("/"))

        start_spider(web_url, thread_number)
        send = {"web_url": web_url, "freq_dict": DIC, "find_webs": list(OUT)}



if __name__ == "__main__":
    main()
    




