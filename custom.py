from bilibili_api import video
import asyncio
import csv
import time
import requests
import os
import shutil
import logging
import unicodedata
from PIL import Image

from config import *

usedTime = time.strftime("%Y%m%d", time.localtime())

def bv2av(bvid):
    time.sleep(0.05)
    site = "https://api.bilibili.com/x/web-interface/view?bvid=" + bvid
    lst = requests.get(site).json()
    if lst["code"] != 0: return "视频不存在！"
    return lst["data"]["aid"]

def real_len(letter):
    if (unicodedata.east_asian_width(letter) in ('F','W','A')):
        return 2
    else:
        return 1

def all_len(text,maxlen):
    ink = 0
    outlen = 0
    for lett in text:
        if outlen < maxlen:
            ink += 1
        outlen += real_len(lett)
    return outlen , ink

def reasons(reasoning):
    reason = []
    for charc in range(len(reasoning)):
        if charc % 14 == 0:
            reason.append(reasoning[charc:charc+14])
    return "\n".join(reason)
customHeader = ['ranking','score','aid','bvid','cid','title','uploader','play','like','coin','star','cover_url','pubtime','k','o_title','sp','st']

with open('data/customed.csv','w',encoding="utf-8-sig", newline='') as csvWrites:
    writer = csv.writer(csvWrites)
    writer.writerow(customHeader)
    async def getInfo(aid,owner):
        if(aid[0] != "A" and aid[0] != "a" and aid[0] == "B"):
            it = bv2av(str(aid[2:]))
        elif(aid[0] in "Aa"):
            it = aid[2:]
        else:
            it = aid
        custAllInfo = video.Video(aid=int(it))
        custed = await custAllInfo.get_info()
        if owner == None or owner == "": # 判断是否指定了作者
            uploader = custed["owner"]["name"]
        else:
            uploader = owner
            shutil.copy("./template/avatar/truck.png",f"./avatar/{custed['aid']}.png")
        # 标题伸缩
        timed = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(custed["pubdate"])))
        allLength , shortRange = all_len(custed["title"],main_max_title * 2)
        if (allLength > main_max_title * 2):
            custtitle = custed["title"][0:shortRange - 1] + "..."
        else:
            custtitle = custed["title"]
        # 列表添加
        oneArr = [
            "","",
            custed["aid"],
            custed["bvid"],
            custed["cid"],
            custtitle,
            uploader,
            custed["stat"]["view"],
            custed["stat"]["like"],
            custed["stat"]["coin"],
            custed["stat"]["favorite"],
            custed["pic"],
            timed,
            "",
            custed["title"]
            ]
        writer.writerow(oneArr)
        logging.info("一个 Custom 作品已记录")
        # 下载头像
        if os.path.exists("avatar/"+ str(custed["aid"]) + ".png"):
            pass
        else:
            face = requests.get(url="https://api.bilibili.com/x/web-interface/view?aid=" + str(custed["aid"])).json()["data"]["owner"]["face"]
            if(face.split(".")[-1] in staticFormat): # 判断静态图片
                with open("avatar/"+ str(custed["aid"]) + ".png", "wb") as f:
                    f.write(requests.get(url=face).content)
            else:
                tempImage = f"avatar/{str(custed['aid'])}.{face.split('.')[-1]}"
                with open(tempImage, "wb") as f:
                    f.write(requests.get(url=face).content)
                    Image.open(tempImage).save("avatar/"+ str(custed['aid']) + ".png")
        # 下载封面
        if os.path.exists("cover/"+ str(custed['aid']) + ".png"):
            pass
        else:
            with open("cover/"+ str(custed['aid']) + ".png", "wb") as f:
                f.write(requests.get(url=custed["pic"]).content)
    if os.path.exists("./custom/custom.csv"):
        with open("custom/custom.csv",encoding="utf-8-sig",newline='') as csvfile:
            custInfo = csv.DictReader(csvfile)
            for cust in custInfo:
                asyncio.get_event_loop().run_until_complete(getInfo(cust["aid"],cust["owner"]))