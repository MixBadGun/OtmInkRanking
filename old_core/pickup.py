from bilibili_api import video
import asyncio
import csv
import time
import requests
import os
import shutil
import logging
from function import get_img,wrap_text
from config import *



def pickData(mainArr):

    allArr = []
    usedTime = time.strftime("%Y%m%d", time.localtime())

    pickHeader = ["aid","bvid","cid","title","reason","uploader","pubtime","full_time","picker"]

    with open('data/picked.csv','w',encoding="utf-8-sig", newline='') as csvWrites:
        writer = csv.writer(csvWrites)
        writer.writerow(pickHeader)
        async def getInfo(aid,reason,owner,picker):
            pickAllInfo = video.Video(aid=int(aid))
            picked = await pickAllInfo.get_info()
            if owner == None or owner == "": # 判断是否指定了作者
                uploader = picked["owner"]["name"]
            else:
                uploader = owner
            timed = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(picked["pubdate"])))
            oneArr = [picked["aid"],picked["bvid"],picked["cid"],picked["title"],reason,uploader,timed,picked["duration"],picker]
            allArr.append(oneArr)
            writer.writerow(oneArr)
            logging.info("一个 Pick Up 作品已记录")
            # 下载头像
            get_img(picked["aid"],True,uploader)
        if os.path.exists("./custom/pick.csv"):
            with open("custom/pick.csv",encoding="utf-8-sig",newline='') as csvfile:
                pickInfo = csv.DictReader(csvfile)
                for pick in pickInfo:
                    if str(pick["aid"]) in mainArr: # 判断主榜是否已经存在 Pick Up 作品
                        continue
                    asyncio.get_event_loop().run_until_complete(getInfo(pick["aid"],wrap_text(pick["reason"],pick_max_reason),pick["owner"],pick["picker"]))
            shutil.move("./custom/pick.csv",f"./data/backup/pick_{usedTime}.csv")
    if len(allArr) == 0:
        os.remove('data/picked.csv')
    return allArr