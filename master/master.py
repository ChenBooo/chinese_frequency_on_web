#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import os
import zmq
import time
import json

linesep = "\n"

def init(wf, sf, cf):
    """输入
    cf:保存字频的cf文件，json格式
    sf:保存已经搜过的url文件，每行为一个url
    wf:等待搜索的url文件，每行为一个url
    返回
    wait_search:待搜索的url集合
    searched：已搜索的url集合
    c_dic:字频字典
    """
    global linesep
    
    if not os.path.exists(wf):
        raise OSError("Please create start url file {0}".format(wf))

    with open(wf, 'r') as fp:
        lines = fp.readlines()
        wait_search = set([x.rstrip(linesep) for x in lines])

    if len(wait_search) == 0:
        raise KeyError("{0} is empty file.".format(wf))

    if os.path.exists(sf):
        with open(sf, 'r') as fp:
            lines = fp.readlines()
            searched = set([x.rstrip(linesep) for x in lines])
    else:
        searched = set()

    if os.path.exists(cf):
        with open(cf, 'r') as fp:
            c_dic = json.load(fp)
    else:
        c_dic = {}

    return wait_search, searched, c_dic

def update(w_url, s_url, c_dic, w_file, s_file, c_file):
    """输入
    w_url:待搜索的url集合
    s_url:已搜索的url集合
    c_dic:字频字典
    信息写入文件中
    w_file:保存待搜索url信息文件
    s_file:保存已搜索url信息文件
    c_file:保存字频信息文件
    """
    global linesep
    
    w_t = linesep.join(w_url)
    with open(w_file, "w") as fp:
        fp.write(w_t)

    s_t = linesep.join(s_url)
    with open(s_file, "w") as fp:
        fp.write(s_t)

    with open(c_file, 'w') as fp:
         json.dump(c_dic, fp, ensure_ascii=False)
         

def main():
    with open("cfg.json") as fp:
        config = json.load(fp)
    
    c_file = config["c_file"]
    s_file = config["s_file"]
    w_file = config["w_file"]
    port = config["port"]
    
    w_url, s_url, c_dic = init(w_file, s_file, c_file)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + str(port))
    print("Serving at port", port)
    
    while True:
    #  Wait for next request from client
        message = socket.recv_json()
        print("receive message:", message)

        if "web_url" in message:
            try:
                dic_ = message["freq_dict"]
                urls = message["find_webs"]
            except KeyError as e:
                print("message damaged.", e)
            else:
                s_url.add(message['web_url'])

                for url in urls:
                    if url not in s_url:
                        w_url.add(url)
                        
                for k, v in dic_.items():
                    if k in c_dic:
                        c_dic[k] += v
                    else:
                        c_dic[k] = 1

                update(w_url, s_url, c_dic, w_file, s_file, c_file)
                print("files update finished.")
                
        if len(w_url) == 0:
            page_url = None
        else:
            page_url = w_url.pop()

        print("response url:", page_url)
        socket.send_json({"web_url": page_url})
        
if __name__ == "__main__":
    main()

                
                
        
