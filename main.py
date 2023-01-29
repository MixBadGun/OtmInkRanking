import logging
import time
import subprocess
import os
import csv
import threading
from moviepy.editor import *
from video_create import MainVideo
from side_create import SideVideo
from pick_create import PickVideo
from all_create import AllVideo
from opening_create import OpeningVideo
logging.basicConfig(format='[%(levelname)s]\t%(message)s',filename="log/" + time.strftime("%Y-%m-%d %H-%M-%S") + '.log', level=logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s]\t%(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel('DEBUG')
logger = logging.getLogger()
logger.addHandler(console_handler)
import danmuku_time

# 精确视频长度

def exactVideoLength(aid):
    tvid = VideoFileClip(f"./video/{aid}.mp4")
    tdur = tvid.duration
    tvid.close()
    return tdur

# 声明变量

from config import *

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

# 封面 & 头像下载

# ranking = 0
# while(ranking < main_end + side_end):
#     vid = ranked_list[ranking]
#     if os.path.exists("cover/"+ str(vid[2]) + ".png"):
#         pass
#     else:
#         with open("cover/"+ str(vid[2]) + ".png", "wb") as f:
#             f.write(requests.get(url=vid[11]).content)
#     if os.path.exists("avatar/"+ str(vid[2]) + ".png"):
#         pass
#     else:
#         face = requests.get(url="https://api.bilibili.com/x/web-interface/view?aid=" + str(vid[2])).json()["data"]["owner"]["face"]
#         if(face.split(".")[-1] in staticFormat): # 判断静态图片
#             with open("avatar/"+ str(vid[2]) + ".png", "wb") as f:
#                 f.write(requests.get(url=face).content)
#         else:
#             tempImage = f"avatar/{vid[2]}.{face.split('.')[-1]}"
#             with open(tempImage, "wb") as f:
#                 f.write(requests.get(url=face).content)
#                 Image.open(tempImage).save("avatar/"+ str(vid[2]) + ".png")
#     ranking += 1

# 视频下载

def getVideo(aid):
    if os.path.exists(f"./video/{aid}.mp4"):
        return
    subprocess.Popen(f'./lux -c ./cookies/cookie.txt -o ./video -O {aid} av{aid}').wait()

# 快速导航导出

# ranks = 0
# for ranked in ranked_list:
#     ranks += 1
#     if ranks > main_end + side_end:
#         break
#     with open(f"./fast_view/bili_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
#         fast.write(f"{ranks}\t{ranked[3]}\n")
#     with open(f"./fast_view/wiki_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
#         fast.write("{{"+f"OtmRanking/brick\n|ranking={ranked[0]}\n|title={ranked[5]}\n|score={ranked[1]}\n|aid={ranked[2]}"+"\n}}\n")

# PICK UP 数据
picked_list = []
if os.path.exists(f"./custom/picked/{usedTime}-picked.csv"):
    pickFile = open(f"./custom/picked/{usedTime}-picked.csv","r",encoding="utf-8-sig")
    pickArr = csv.reader(pickFile)
    ok = 0
    for sti in pickArr:
        if ok == 0:
            ok += 1
            continue
        picked_list.append(sti)

# PICK UP 快速导航

# picks = 0
# for pickOne in pickArr:
#     picks += 1
#     with open(f"./fast_view/bili_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
#         fast.write(f"{picks}\t{pickOne[1]}\n")
#     with open(f"./fast_view/wiki_{usedTime}.txt","a",encoding="utf-8-sig") as fast:
#         fast.write("{{"+f"OtmRanking/brick\n|ranking={picks}\n|title={pickOne[3]}\n|score=PICK UP\n|aid={pickOne[0]}"+"\n}}\n")

#  根据生成的表格生成图片

# ## 主榜
# subprocess.Popen('start /wait TEditor.exe batchgen -i "template/main.ted" -d "custom/data.CSV" -o "output_image/main" -n "MainRank_{index}" -s 1 -e ' + str(main_end),shell=True).wait()
# logging.info('主榜图片合成完毕')
# ## 副榜
# subprocess.Popen('start /wait TEditor.exe batchgen -i "template/side.ted" -d "custom/data.CSV" -o "output_image/side" -n "SideRank_{index}" -s ' + str(main_end+1) + ' -e ' + str(main_end+side_end) + ' -y 251 -r 3',shell=True).wait()
# logging.info('副榜图片合成完毕')
# ## PICK UP
# if os.path.exists("./custom/picked.csv"):
#     subprocess.Popen('start /wait TEditor.exe batchgen -i "template/pick.ted" -d "data/picked.CSV" -o "output_image/pick" -n "PickRank_{index}" -s 1 -e '+ str(len(pickArr)),shell=True).wait()
#     logging.info('Pick Up 图片合成完毕')

# 主榜段落合成
muitl_render = []
for viding in ranked_list:
    ranking = int(viding[0])
    if ranking > main_end:
        break
    if os.path.exists(f"./output_clips/MainRank_{ranking}.mp4"):
        continue
    aid = viding[2]
    bvid = viding[3]
    cid = viding[4]
    getVideo(aid)
    full_time = exactVideoLength(aid)
    start_time,end_time = danmuku_time.danmuku_time(aid,cid,full_time,sep_time)
    muitl_limit.acquire()
    single_render = threading.Thread(target=MainVideo,args=(aid,start_time,end_time,ranking))
    single_render.start()
    muitl_render.append(single_render)
for fg in muitl_render:
    fg.join()

# 副榜段落合成
if os.path.exists("./output_clips/SideRank.mp4"):
    pass
else:
    SideVideo(main_end,side_end,side_count)

# PICK UP 合成
picks = 0
muitl_render = []
for picking in picked_list:
    picks += 1
    if os.path.exists(f"./output_clips/PickRank_{picks}.mp4"):
        continue
    aid = picking[0]
    bvid = picking[1]
    cid = picking[2]
    getVideo(aid)
    full_time = exactVideoLength(aid)
    start_time,end_time = danmuku_time.danmuku_time(aid,cid,full_time,sep_time)
    muitl_limit.acquire()
    single_render = threading.Thread(target=PickVideo,args=(aid,start_time,end_time,picks))
    single_render.start()
    muitl_render.append(single_render)
for fg in muitl_render:
    fg.join()

# 开头简要合成
if os.path.exists("./output_clips/Opening.mp4"):
    pass
else:
    OpeningVideo(usedTime)

# 总拼接

AllVideo(main_end,pickArr,usedTime)