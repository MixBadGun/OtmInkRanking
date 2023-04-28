import csv
import asyncio
from PIL import Image
import shutil
import logging
import subprocess
from moviepy.editor import *
from bilibili_api import video
from function import get_img,wrap_text
# import git

# 声明变量

from config import *

# repo = git.Repo.init(path='./custom')

# 获取数据
ranked_list = []
datafile = open("custom/data.csv","r",encoding="utf-8-sig")
ranked_lists = csv.reader(datafile)
ok = 0
for sti in ranked_lists:
    if ok == 0:
        ok += 1
        continue
    ranked_list.append(sti)
mainArr = []
ignum = 0
for ig in ranked_list:
    ignum += 1
    if ignum > main_end:
        break
    mainArr.append(str(ig[2]))

# 主榜封面 & 头像下载

ranking = 0
while(ranking < main_end):
    vid = ranked_list[ranking]
    get_img(vid[2])
    ranking += 1
while(ranking < main_end + side_end):
    vid = ranked_list[ranking]
    get_img(vid[2],side = True)
    ranking += 1

# 快速导航导出

ranks = 0
for ranked in ranked_list:
    ranks += 1
    if ranks > main_end + side_end:
        break
    with open(f"./fast_view/bili_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
        fast.write(f"{ranks}\t{ranked[3]}\n")
    with open(f"./fast_view/wiki_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
        fast.write("{{"+f"OtmRanking/brick\n|ranking={ranked[0]}\n|title={ranked[14]}\n|score={ranked[1]}\n|aid={ranked[2]}"+"\n}}\n")

# Pick Up

allArr = []
usedTime = time.strftime("%Y%m%d", time.localtime())

pickHeader = ["aid","bvid","cid","title","reason","uploader","pubtime","full_time","picker"]

with open(f"./custom/picked/{usedTime}-picked.csv",'w',encoding="utf-8-sig", newline='') as csvWrites:
    writer = csv.writer(csvWrites)
    writer.writerow(pickHeader)
    async def getInfo(aid,reason,owner,picker):
        pickAllInfo = video.Video(aid=int(aid))
        picked = await pickAllInfo.get_info()
        if owner == None or owner == "": # 判断是否指定了作者
            uploader = picked["owner"]["name"]
        else:
            uploader = owner
            shutil.copy("./template/avatar/truck.png",f"./avatar/{picked['aid']}.png")
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
if len(allArr) == 0:
    os.remove(f"./custom/picked/{usedTime}-picked.csv")

# PICK UP 快速导航
picks = 0
for pickOne in allArr:
    picks += 1
    with open(f"./fast_view/bili_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
        fast.write(f"{picks}\t{pickOne[1]}\n")
    with open(f"./fast_view/wiki_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
        fast.write("{{"+f"OtmRanking/brick\n|ranking={picks}\n|title={pickOne[3]}\n|score=PICK UP\n|aid={pickOne[0]}"+"\n}}\n")

#  根据生成的表格生成图片

## 主榜
subprocess.Popen('start /wait TEditor.exe batchgen -i "template/main.ted" -d "custom/data.CSV" -o "custom/output_image/main" -n "MainRank_{index}" -s 1 -e ' + str(main_end),shell=True).wait()
logging.info('主榜图片合成完毕')
## 副榜
subprocess.Popen('start /wait TEditor.exe batchgen -i "template/side.ted" -d "custom/data.CSV" -o "custom/output_image/side" -n "SideRank_{index}" -s ' + str(main_end+1) + ' -e ' + str(main_end+side_end) + ' -y 251 -r 3',shell=True).wait()
logging.info('副榜图片合成完毕')
## PICK UP
if os.path.exists(f"./custom/picked/{usedTime}-picked.csv"):
    subprocess.Popen(f'start /wait TEditor.exe batchgen -i "template/pick.ted" -d "custom/picked/{usedTime}-picked.csv" ' + '-o "custom/output_image/pick" -n "PickRank_{index}" -s 1 -e '+ str(len(allArr)),shell=True).wait()
    logging.info('Pick Up 图片合成完毕')

# 图片转换

for curDir, dirs, files in os.walk("./custom/output_image/"):
    for file in files:
        usingpath = f"{curDir}/{file}"
        Image.open(usingpath).save(usingpath)

# 上载到 GitHub
# repo.index.add(items="*")
# repo.index.commit("new files")
# remote = repo.remote(name='github')
# remote.push()