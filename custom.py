from bilibili_api import video
import asyncio
import csv
import time
import os
import shutil
import logging
from function import turnAid , short_text , get_img

from config import *

usedTime = time.strftime("%Y%m%d", time.localtime())

customHeader = ['ranking','score','aid','bvid','cid','title','uploader','play','like','coin','star','cover_url','pubtime','k','o_title','sp','st']

with open('data/customed.csv','w',encoding="utf-8-sig", newline='') as csvWrites:
    writer = csv.writer(csvWrites)
    writer.writerow(customHeader)
    async def getInfo(aid,owner):
        it = turnAid(aid)
        custAllInfo = video.Video(aid=int(it))
        custed = await custAllInfo.get_info()
        if owner == None or owner == "": # 判断是否指定了作者
            uploader = custed["owner"]["name"]
        else:
            uploader = owner
            shutil.copy("./template/avatar/truck.png",f"./avatar/{custed['aid']}.png")
        # 标题伸缩
        timed = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(custed["pubdate"])))
        custtitle = short_text(custed["title"],main_max_title)
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
        # 下载头像 & 封面
        get_img(custed["aid"],True)
        # 下载封面
    if os.path.exists("./custom/custom.csv"):
        with open("custom/custom.csv",encoding="utf-8-sig",newline='') as csvfile:
            custInfo = csv.DictReader(csvfile)
            for cust in custInfo:
                asyncio.get_event_loop().run_until_complete(getInfo(cust["aid"],cust["owner"]))