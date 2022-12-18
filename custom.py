from bilibili_api import video
import asyncio
import csv
import time
import requests
import os
import shutil
import logging

usedTime = time.strftime("%Y%m%d", time.localtime())

def reasons(reasoning):
    reason = []
    for charc in range(len(reasoning)):
        if charc % 14 == 0:
            reason.append(reasoning[charc:charc+14])
    return "\n".join(reason)
customHeader = ['ranking','score','aid','bvid','cid','title','uploader','play','like','coin','star','cover_url','pubtime','k']

with open('data/customed.csv','w',encoding="utf-8-sig", newline='') as csvWrites:
    writer = csv.writer(csvWrites)
    writer.writerow(customHeader)
    async def getInfo(aid,owner):
        custAllInfo = video.Video(aid=int(aid))
        custed = await custAllInfo.get_info()
        if owner == None or owner == "": # 判断是否指定了作者
            uploader = custed["owner"]["name"]
        else:
            uploader = owner
            shutil.copy("./template/avatar/truck.png",f"./avatar/{custed['aid']}.png")
        timed = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(custed["pubdate"])))
        oneArr = [
            "","",
            custed["aid"],
            custed["bvid"],
            custed["cid"],
            custed["title"],
            uploader,
            custed["stat"]["view"],
            custed["stat"]["like"],
            custed["stat"]["coin"],
            custed["stat"]["favorite"],
            custed["pic"],
            timed,
            ""
            ]
        writer.writerow(oneArr)
        logging.info("一个 Custom 作品已记录")
        # 下载头像
        face = requests.get(url="https://api.bilibili.com/x/web-interface/view?aid=" + str(custed["aid"])).json()["data"]["owner"]["face"]
        if os.path.exists("avatar/"+ str(custed["aid"]) + ".png"):
            pass
        else:
            with open("avatar/"+ str(custed["aid"]) + ".png", "wb") as f:
                f.write(requests.get(url=face).content)
    if os.path.exists("./custom/custom.csv"):
        with open("custom/custom.csv",encoding="utf-8-sig",newline='') as csvfile:
            custInfo = csv.DictReader(csvfile)
            for cust in custInfo:
                asyncio.get_event_loop().run_until_complete(getInfo(cust["aid"],cust["owner"]))