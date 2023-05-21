import csv
import time
import logging
import os
from config import *
from auto_pipeline import all_video_info , aid_to_score_norm
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
    for video in all_video_info:
        if int(all_video_info[video]["aid"]) in blackArr:
            continue
        if int(all_video_info[video]["owner"]["mid"]) in adjust_dic:
            normk = float(adjust_dic[all_video_info[video]["owner"]["mid"]])
        else:
            normk = 1
        if str(all_video_info[video]["copyright"]) not in ["1",1]:
            author_name = "转载"
        else:
            author_name = str(all_video_info[video]["owner"]["name"])
        norm_score = float('%.3f' % (aid_to_score_norm[all_video_info[video]["aid"]] * normk))
        vid_list.append([
            norm_score,
            str(all_video_info[video]["aid"]),
            str(all_video_info[video]["bvid"]),
            str(all_video_info[video]["cid"]),
            str(all_video_info[video]["title"]),
            author_name,
            str(all_video_info[video]["stat"]["view"]),
            str(all_video_info[video]["stat"]["like"]),
            str(all_video_info[video]["stat"]["coin"]),
            str(all_video_info[video]["stat"]["favorite"]),
            str(all_video_info[video]["pic"]),
            time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(all_video_info[video]["pubdate"]))),
            str(normk),
            str(all_video_info[video]["title"]),
            '1',
            '',
            str(all_video_info[video]["copyright"]),
            str(all_video_info[video]["owner"]["name"])
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