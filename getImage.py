import requests
import re
from PIL import Image
from io import BytesIO
import random
import getCAPTCHA
import time


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'cookie': cookie     # 这里记得填上自己的cookie
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'cookie': cookie     # 这里记得填上自己的cookie
    }
    im = getImg(id)
    code = getCAPTCHA.getCode(im)
    print(code)
    data = {
        "data": examType + "," + id + "," + name,
        "v": code
    }

    # 爬取的延时时间，这里是100ms，尽量设个时间，降低对服务器的压力
    time.sleep(0.01)
    global correct, error
    try:
        r = requests.post(url, data=data, headers=header)
        r.raise_for_status()
        if "验证码错误" in r.text:
            error += 1
            print(r.text)
            im.save("raw_error2/" + code + ".png")
        else:
            correct += 1
            print(id + "\t" + examType + "\r" + r.text)  # 返回id和服务器中的信息
            im.save("raw_correct2/" + code + ".png")
        return r.text
    except Exception as e:
        print("Exception: " + repr(e))


if __name__ == '__main__':
    start = 1  # 开头的考场号
    end = 300  # 结束的考场号
    name = "小王"  # 姓名
    id_pre = "4200901811"  # 准考证号前十位
    correct = 0
    error = 0

    # 抓包拿一下自己的cookie
    cookie = ''

    # 抓包分析得到的POST方法的部分参数
    if id_pre[9] == '1':
        examType = 'CET4_181_DANGCI'
    else:
        examType = 'CET6_181_DANGCI'

    # 获取多少张验证码
    for i in range(10):
        query("420090181100101", examType, name)

    print("correct: " + str(correct), "error: " + str(error))
    print("accuracy: %.2f%%" % (correct * 100 / (correct + error)))
