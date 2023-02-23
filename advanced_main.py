import csv
import time
import logging
import os
import unicodedata
from config import *
from auto_pipeline import all_video_info , aid_to_score_norm
import shutil
# 新建文件夹

dirpaths = ["avatar","cover","custom","data","fast_view","fonts","log","output_all","output_clips","custom/output_image","custom/output_image/main","custom/output_image/pick","custom/output_image/side","video","cookies","fast_check","fast_check/source"]
for dirpath in dirpaths:
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

# 字符长度判断

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

# 预先黑名单
blackArr = []
with open("custom/blacklist.csv",encoding="utf-8-sig",newline='') as blackfile:
    blackInfo = csv.DictReader(blackfile)
    for bl in blackInfo:
        blackArr.append(int(bl["aid"]))
# 预先内容调整
adjust_dic = {}
with open("custom/adjust.csv",encoding="utf-8-sig",newline='') as adjustfile:
    adjustInfo = csv.DictReader(adjustfile)
    for adj in adjustInfo:
        adjust_dic[int(adj["uid"])] = adj["k"]

co_header = ['ranking','score','aid','bvid','cid','title','uploader','play','like','coin','star','cover_url','pubtime','k','o_title']
logging.info('生成 TEditor CSV 表格')
with open("custom/data.csv","w",encoding="utf-8-sig",newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(co_header)
    vid_list = []
    for video in all_video_info:
        if int(all_video_info[video]["aid"]) in blackArr:
            continue
        if int(all_video_info[video]["owner"]["mid"]) in adjust_dic:
            normk = float(adjust_dic[all_video_info[video]["owner"]["mid"]])
        else:
            normk = 1
        norm_score = float('%.3f' % (aid_to_score_norm[all_video_info[video]["aid"]] * normk))
        vid_list.append([
            norm_score,
            str(all_video_info[video]["aid"]),
            str(all_video_info[video]["bvid"]),
            str(all_video_info[video]["cid"]),
            str(all_video_info[video]["title"]),
            str(all_video_info[video]["owner"]["name"]),
            str(all_video_info[video]["stat"]["view"]),
            str(all_video_info[video]["stat"]["like"]),
            str(all_video_info[video]["stat"]["coin"]),
            str(all_video_info[video]["stat"]["favorite"]),
            str(all_video_info[video]["pic"]),
            time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(all_video_info[video]["pubdate"]))),
            str(normk),
            str(all_video_info[video]["title"])
        ])
    vid_list = sorted(vid_list,key=lambda x:x[0],reverse=True)
    ranking = 0
    ranked_list = []
    for vid in vid_list:
        ranking += 1
        # 过滤结合字符
        vid[4] = passMn(vid[4])
        # 判断长度进行伸缩
        if (ranking <= main_end):
            allLength , shortRange = all_len(vid[4],main_max_title * 2)
            if (allLength > main_max_title * 2):
                vid[4] = vid[4][0:shortRange - 2] + "..."
        elif (ranking <= main_end + side_end):
            allLength , shortRange = all_len(vid[4],side_max_title * 2)
            if (allLength > side_max_title * 2):
                vid[4] = vid[4][0:shortRange - 2] + "..."
        # 简易start_time判断
        ranked_list.append([ranking] + vid)
    writer.writerows(ranked_list)
shutil.copy("./custom/data.csv","./fast_check/source/data.csv")