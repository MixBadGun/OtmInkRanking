from bilibili_api import video
import asyncio
import csv
import time
import requests
import os
import shutil
import logging
import unicodedata
from config import *

def real_len(letter):
    if (unicodedata.east_asian_width(letter) in ('F','W','A')):
        return 2
    else:
        return 1

def pickData(mainArr):

    allArr = []
    usedTime = time.strftime("%Y%m%d", time.localtime())

    def reasons(reasoning):
        reason = ""
        max_n = 0
        for charc in reasoning:
            if charc == "\n":
                max_n = 0
                reason += "\n"
                continue
            if max_n >= pick_max_reason:
                reason += "\n"
                max_n = 0
            reason += charc
            max_n += real_len(charc)
        return reason
    pickHeader = ["aid","bvid","cid","title","reason","uploader","pubtime","full_time"]

    with open('data/picked.csv','w',encoding="utf-8-sig", newline='') as csvWrites:
        writer = csv.writer(csvWrites)
        writer.writerow(pickHeader)
        async def getInfo(aid,reason,owner):
            pickAllInfo = video.Video(aid=int(aid))
            picked = await pickAllInfo.get_info()
            if owner == None or owner == "": # 判断是否指定了作者
                uploader = picked["owner"]["name"]
            else:
                uploader = owner
                shutil.copy("./template/avatar/truck.png",f"./avatar/{picked['aid']}.png")
            timed = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(picked["pubdate"])))
            oneArr = [picked["aid"],picked["bvid"],picked["cid"],picked["title"],reason,uploader,timed,picked["duration"]]
            allArr.append(oneArr)
            writer.writerow(oneArr)
            logging.info("一个 Pick Up 作品已记录")
            # 下载头像
            face = requests.get(url="https://api.bilibili.com/x/web-interface/view?aid=" + str(picked["aid"])).json()["data"]["owner"]["face"]
            if os.path.exists("avatar/"+ str(picked["aid"]) + ".png"):
                pass
            else:
                with open("avatar/"+ str(picked["aid"]) + ".png", "wb") as f:
                    f.write(requests.get(url=face).content)
        if os.path.exists("./custom/pick.csv"):
            with open("custom/pick.csv",encoding="utf-8-sig",newline='') as csvfile:
                pickInfo = csv.DictReader(csvfile)
                for pick in pickInfo:
                    if str(pick["aid"]) in mainArr: # 判断主榜是否已经存在 Pick Up 作品
                        continue
                    asyncio.get_event_loop().run_until_complete(getInfo(pick["aid"],reasons(pick["reason"]),pick["owner"]))
            shutil.move("./custom/pick.csv",f"./data/backup/pick_{usedTime}.csv")
    return allArr