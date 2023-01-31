import logging
import time
import subprocess
import os
import csv
import ffmpeg
from moviepy.editor import *
from video_create_ff import MainVideo
from side_create_ff import SideVideo
from pick_create_ff import PickVideo
from all_create_ff import AllVideo
from opening_create_ff import OpeningVideo
logging.basicConfig(format='[%(levelname)s]\t%(message)s',filename="log/" + time.strftime("%Y-%m-%d %H-%M-%S") + '.log', level=logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s]\t%(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel('DEBUG')
logger = logging.getLogger()
logger.addHandler(console_handler)
import danmuku_time

# 新建文件夹

dirpaths = ["avatar","cover","custom","data","fast_view","fonts","log","output_all","output_clips","output_image","video","cookies"]
for dirpath in dirpaths:
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

# 精确视频长度

def exactVideoLength(aid):
    tdur = float(ffmpeg.probe(f"./video/{aid}.mp4")["streams"][0]["duration"])
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

# 视频下载
def getVideo(aid):
    command = ["./lux"]
    if os.path.exists(f"./cookies/cookie.txt"):
        command.append("-c")
        command.append("./cookies/cookie.txt")
    if os.path.exists(f"./video/{aid}.mp4"):
        return
    subprocess.Popen(command + ["-o","./video","-O",aid,f"av{aid}"]).wait()

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

AllVideo(main_end,picked_list,usedTime)