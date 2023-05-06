import requests
import logging
import subprocess
import codecs
import csv
import ffmpeg
from io import BytesIO
from PIL import Image
import unicodedata
from config import *

def wrap_text(text,max_letter = 20,all_max = 10000):
    reason = ""
    max_n = 0
    for charc in text:
        if charc == "\n":
            max_n = 0
            reason += "\n"
            continue
        if max_n >= max_letter:
            reason += "\n"
            max_n = 0
        reason += charc
        max_n += real_len(charc)
    reason = short_text(reason,all_max)
    return reason

def real_len(letter):
    widLetter = "ABCDEFGHJKLMNOPQRSTUVWXYZm"
    NarrowLetter = "Iijl()[].;:!\'\"`{}"
    if letter in widLetter:
        return 1.5
    if letter in NarrowLetter:
        return 0.5
    if (unicodedata.east_asian_width(letter) in ('F','W','A')):
        return 2
    else:
        return 1

def passMn(text):
    outsil = ""
    for sil in text:
        if unicodedata.category(sil) != "Mn":
            outsil += sil
    return outsil

def all_len(text,maxlen):
    ink = 0
    outlen = 0
    for lett in text:
        if outlen < maxlen:
            ink += 1
        outlen += real_len(lett)
    return outlen , ink

def get_img(aid,stored = False,uploader = "None",side = False):
    video_data = requests.get(url=f"https://api.bilibili.com/x/web-interface/view?aid={aid}").json()
    if video_data["code"] != 0:
        logging.error(f"检测到 av{aid} 的视频状态异常！请确认该视频状态，若有问题则可以立即退出本程序。否则按回车键继续。")
        input()
    face = video_data["data"]["owner"]["face"]
    cover = video_data["data"]["pic"]
    # 头像
    if not os.path.exists(f"avatar/{aid}.png"):
        ava_size = avatar_size if not side else side_avatar_size
        if stored:
            if os.path.exists(f"./preavatar/{uploader}.png"):
                avatar_src = f"./preavatar/{uploader}.png"
            else:
                avatar_src = "./template/avatar/truck.png"
            img = Image.open(avatar_src)
            img_scaled = img.resize(ava_size,Image.ANTIALIAS)
            img_scaled.save(f"./avatar/{aid}.png")
        else:
            img_content = requests.get(url=face).content
            img = Image.open(BytesIO(img_content))
            img_scaled = img.resize(ava_size,Image.ANTIALIAS)
            img_scaled.save(f"avatar/{aid}.png")
    # 封面
    if not os.path.exists(f"cover/{aid}.png"):
        img_content = requests.get(url=cover).content
        img = Image.open(BytesIO(img_content))
        size = cover_size if not side else side_cover_size
        img_scaled = img.resize(size,Image.ANTIALIAS)
        img_scaled.save(f"cover/{aid}.png")

def getVideo(aid):
    subprocess.Popen(f'lux -c ./cookies/cookie.txt -o ./fast_check/ -O ed av{aid}').wait()

def turnAid(id):
    if ("av" in id) or ("AV" in id):
        return id[2:]
    elif ("BV" in id):
        site = "https://api.bilibili.com/x/web-interface/view?bvid=" + id
        lst = codecs.decode(requests.get(site).content, "utf-8").split("\"")
        return str(lst[16][1:-1])

def short_text(text,max_lenth = 20):
    allLength , shortRange = all_len(text,max_lenth * 2)
    if (allLength > max_lenth * 2):
        text = text[0:shortRange - 2] + "..."
    return text

# 精确视频长度

def exactVideoLength(aid):
    tdur = float(ffmpeg.probe(f"./video/{aid}.mp4")["streams"][0]["duration"])
    return tdur

# 视频下载

def getVideo(aid,part = 1):
    command = ["./lux"]
    if part > 1:
        p_src = f"?p={part}"
    else:
        p_src = ""
    if os.path.exists(f"./cookies/cookie.txt"):
        command.append("-c")
        command.append("./cookies/cookie.txt")
    if os.path.exists(f"./video/{aid}.mp4"):
        return
    subprocess.Popen(command + ["-o","./video","-O",aid,f"av{aid}{p_src}"]).wait()

def convert_csv(file):
    outlist = []
    with open(file,"r",encoding="utf-8-sig") as datafile:
        lists = csv.reader(datafile)
        ok = 0
        for sti in lists:
            if ok == 0:
                ok += 1
                continue
            outlist.append(sti)
    return outlist