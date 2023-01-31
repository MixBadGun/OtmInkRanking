import logging
import requests
import math
from lxml import html

def danmuku_time(aid,cid,full_time,sep_time):
    # 查询是否存在高能进度条
    try:
        high_enerbar = requests.get('http://bvc.bilivideo.com/pbp/data?cid='+str(cid)).json()
        high_enerbar_info = high_enerbar["events"]["default"]
        high_sec = high_enerbar["step_sec"]
        high_index = (high_enerbar_info.index(max(high_enerbar_info)) + 1)*high_sec - 1
        logging.info('获取到 av' + str(aid) + ' 视频的高能进度条起始时间为 ' + str(high_index) + " 秒")
    except:
        # 不存在则进行弹幕稀疏程度计算
        logging.info('未获取到 av' + str(aid) + ' 视频的高能进度条')
        high_danmuku_array = []
        high_enerbar = html.fromstring(requests.get('http://api.bilibili.com/x/v1/dm/list.so?oid='+str(cid)).content)
        for high_danmuku in high_enerbar:
            if high_danmuku.tag == "d":
                high_danmuku_time = math.floor(float(high_danmuku.get("p").split(",")[0]))
                high_danmuku_array.append(high_danmuku_time)
        if len(high_danmuku_array) == 0:
            logging.info('获取到 av' + str(aid) + ' 视频的弹幕数为 0')
            high_index = full_time/2
            logging.info('获取 av' + str(aid) + ' 视频的一半长度为起始时间')
        else:
            # 计算出现最多弹幕的时间段
            high_max = 0
            for high_int in high_danmuku_array:
                high_con = high_danmuku_array.count(high_int)
                if high_con > high_max:
                    high_max = high_con
                    high_max_time = high_int
            high_index = high_max_time - 1
    logging.info('获取 av' + str(aid) + ' 视频的起始时间为 ' + str(high_index) + " 秒")
    if high_index < (full_time * 0.05):
        high_index = full_time * 0.05
        logging.info('获取 av' + str(aid) + ' 视频的起始时间过前，调整往后')
    if full_time - high_index < sep_time:
        high_index = full_time - sep_time * 1.35
        logging.info('获取 av' + str(aid) + ' 视频的起始时间过短，改为前移')
    if high_index < 0:
        high_index = 0
        logging.info('获取 av' + str(aid) + ' 视频的起始时间为负，改为 0 秒开始')
    logging.info('最终获取 av' + str(aid) + ' 视频的起始时间为 ' + str(high_index) + " 秒")

    if full_time < sep_time:
        end_index = full_time
    else:
        end_index = sep_time

    return high_index,end_index