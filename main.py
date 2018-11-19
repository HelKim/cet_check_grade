import requests
import random
import re
from PIL import Image
from io import BytesIO
import getCAPTCHA
import time
import threading
import queue
import os


def getImg(id):
    '''
    获取验证码图片
    :param id: 考号
    :return:
            im: 验证码图片
    '''
    global cookie
    getImgUrl = 'http://cache.neea.edu.cn/Imgs.do?c=CET&ik=' + id + '&t=' + str(random.random())
    img_header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'cache.neea.edu.cn',
        'Referer': 'http://cet.neea.edu.cn/cet/',
        'User-Agent': 'Mozilla/5.0',
        'cookie': cookie  # 这里记得填上自己的cookie
    }

    def get():
        r = requests.get(getImgUrl, headers=img_header, timeout=5)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        url = re.findall(r'"(.*?)"', r.text)[0]
        print(url)
        imgr = requests.get(url, timeout=5)
        imgr.raise_for_status()
        return imgr.content
    im_content = None
    while im_content is None:
        try:
            im_content = get()
            im = Image.open(BytesIO(im_content))
            return im
        except Exception as e:
            print(repr(e))
            continue


def query(id, examType, name):
    '''
    查询
    :param id: 考号
    :param examType: 考试类型
    :param name: 姓名
    :return:
    '''
    global cookie
    url = "http://cache.neea.edu.cn/cet/query"
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '75',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'cache.neea.edu.cn',
        'Origin': 'http://cet.neea.edu.cn',
        'Referer': 'http://cet.neea.edu.cn/cet',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0',
        'cookie': cookie     # 这里记得填上自己的cookie
    }
    flag = True
    while flag:
        im = getImg(id)
        code = getCAPTCHA.getCode(im)
        print(code)
        data = {
            "data": examType + "," + id + "," + name,
            "v": code
        }

        # 爬取的延时时间，这里是100ms，尽量设个时间，降低对服务器的压力
        # time.sleep(0.1)

        try:
            r = requests.post(url, data=data, headers=header)
            r.raise_for_status()
            if "验证码错误" in r.text:
                print(r.text)
                continue
            else:
                print(id + "\t" + examType + "\r" + r.text)  # 返回id和服务器中的信息
                return r.text
        except Exception as e:
            print("Exception: " + repr(e))
            continue


def result_table(data):
    id = re.findall(r"{z:'(.*?)',n:",data)
    name = re.findall(r"n:'(.*?)',x:",data)
    school = re.findall(r",x:'(.*?)',s:", data)
    all = re.findall(r",s:(.*?),t:", data)
    listen = re.findall(r",l:(.*?),r:", data)
    read = re.findall(r",r:(.*?),w:", data)
    write = re.findall(r",w:(.*?),kyz", data)
    result = "准考证号:\t" + id[0] + "\n姓   名:\t" + name[0] + "\n学   校:\t" + school[0] + "\n听   力:\t" + listen[0]\
             + "\n阅   读:\t" + read[0] + "\n写   作:\t" + write[0] + "\n总   分:\t"+ all[0]
    return result


# 单线程版
def let_we_go(id_pre, examType, name, start, end):
    for i in range(start, end + 1):
        k = str(i)
        if i < 10:
            k = "00" + k
        elif i < 100:
            k = "0" + k
        for j in range(1, 31):
            x = str(j)
            if j < 10:
                x = "0" + x
            idnum = id_pre + k + x
            print(idnum)
            text = query(idnum, examType, name)
            if idnum in text:
                print(result_table(text))
                with open(os.path.join(result_path, name + "-" + str(idnum) + ".txt"), "w") as f:
                    f.write(result_table(text))  # 查到存成绩
                return


_queue = queue.Queue()      # 线程队列
_thread_flag = True     # 线程标志


# 线程函数
def go_thread(examType, name):
    global _thread_flag, _queue, result_path
    while _thread_flag and not _queue.empty():
        try:
            idnum = _queue.get()
            text = query(idnum, examType, name)
            if idnum in text:
                print(result_table(text))
                with open(os.path.join(result_path, name + "-" + str(idnum) + ".txt"), "w") as f:
                    f.write(result_table(text))  # 查到存成绩
                    _thread_flag = False
                return
        except Exception as e:
            print(repr(e))
            break


# 多线程版，这里是4线程
def let_we_go_multi(id_pre, examType, name, start, end):
    global _queue, result_path
    for i in range(start, end + 1):
        k = str(i)
        if i < 10:
            k = "00" + k
        elif i < 100:
            k = "0" + k
        for j in range(1, 31):
            x = str(j)
            if j < 10:
                x = "0" + x
            idnum = id_pre + k + x
            _queue.put(idnum)

    # 这段是第一个先在主线程执行，keras多线程运行模型有问题，目前只知道先在主线程执行一次可以解决
    temp = _queue.get()
    text = query(temp, examType, name)
    if temp in text:
        print(result_table(text))
        with open(os.path.join(result_path, name + "-" + str(temp) + ".txt"), "w") as f:
            f.write(result_table(text))  # 查到存成绩
        return

    global thread_num
    thread_list = []
    for i in range(thread_num):
        t = threading.Thread(target=go_thread, args=(examType, name))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()


if __name__ == '__main__':
    start = 1  # 开头的考场号
    end = 300  # 结束的考场号
    name = "小王"  # 姓名
    id_pre = "4404801812"  # 准考证号前十位
    # 抓包拿一下自己的cookie
    cookie = ''

    # 抓包分析得到的POST方法的部分参数
    if id_pre[9] == '1':
        examType = 'CET4_181_DANGCI'
    else:
        examType = 'CET6_181_DANGCI'

    result_path = 'result'
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    thread_num = 4  # 线程数
    # time_start1 = time.time()
    # let_we_go(id_pre, examType, name, start, end)
    # time_end1 = time.time()
    time_start2 = time.time()
    let_we_go_multi(id_pre, examType, name, start, end)
    time_end2 = time.time()
    # print('totally cost1: ', time_end1 - time_start1)
    print('totally cost2: ', time_end2 - time_start2)
