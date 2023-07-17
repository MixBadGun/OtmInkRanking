import csv
import time
import logging
import os
from config import *
from get_video_info_score import aid_to_score_norm, selected_video_stat, all_video_info
from function import passMn,short_text
import shutil
# 新建文件夹

dirpaths = ["avatar","cover","custom","data","fast_view","fonts","log","output_all","output_clips","custom/output_image","custom/output_image/main","custom/output_image/pick","custom/output_image/side","video","cookies","fast_check","fast_check/source","preavatar"]
for dirpath in dirpaths:
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

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

co_header = ['ranking','score','aid','bvid','cid','title','uploader','play','like','coin','star','cover_url','pubtime','k','o_title','sp','st','copyright','o_name']
logging.info('生成 TEditor CSV 表格')
with open("custom/data.csv","w",encoding="utf-8-sig",newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(co_header)
    vid_list = []
    for video_aid, video_info in all_video_info.items():
        video_stat = selected_video_stat.get(video_aid, {})
        if int(video_aid) in blackArr:
            continue
        normk = adjust_dic.get(int(video_info["mid"]), 1)
        if "copyright" not in video_stat:
            author_name = f"{video_info['author']} | 未指定"
        elif str(video_stat["copyright"]) != "1":
            author_name = f"{video_info['author']} | 转载"
        else:
            author_name = str(video_info["author"])
        norm_score = float('%.3f' % (aid_to_score_norm[video_aid] * normk))
        vid_list.append([
            norm_score,
            str(video_aid),
            str(video_info["bvid"]),
            "", # 两个新 api 都没返回 cid
            str(video_info["title"]),
            author_name,
            str(video_info["play"]),
            str(video_stat.get("like", "未取得")),
            str(video_stat.get("coin", "未取得")),
            str(video_stat.get("favorites", "未取得")),
            str(video_info["pic"]),
            str(video_info["pubdate"]),
            str(normk),
            str(video_info["title"]),
            '1',
            '',
            str(video_stat.get("copyright", "未取得")),
            str(video_info['author'])
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
            vid[4] = short_text(vid[4],main_max_title)
        elif (ranking <= main_end + side_end):
            vid[4] = short_text(vid[4],side_max_title)
        ranked_list.append([ranking] + vid)
    writer.writerows(ranked_list)
shutil.copy("./custom/data.csv","./fast_check/source/data.csv")