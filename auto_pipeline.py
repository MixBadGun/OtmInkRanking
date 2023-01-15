import json
import os
from typing import List,Tuple,Dict,Union,Optional,Any
import marshal
import pickle
import datetime
import logging
from collections import defaultdict
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s@%(funcName)s: %(message)s')

from auto_pipeline_func import *

str_time = datetime.datetime.now().strftime('%y%m%d') # 今天日期
delta_days = 10 # 以今天往前的第 delta_days 日开始统计
range_days = 7 # 统计 range_days 天的数据
base_path = "./AutoData/"   # 数据存储路径

video_zones = [22]
# 鬼畜: 119（不要用这个）; 音 MAD: 26; 人力: 126; 鬼调: 22
# 见 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/video/video_zone.md

# 其实这些关键词的影响并不大
target_good_key_words = [
    "fuxi","复习","複習","fx","高技术","好听","好汀","好聽","喜欢","喜歡","支持","漂亮","舒服"
    "死了","厉害","厲害","最好","最高","最佳","订餐","sk","suki","suang","爽",
    "不错","不錯","牛逼","牛批","nb","！！！","神作","帅","帥","触","觸","强","強","棒",
    "tql","wsl","yyds","永远的神","谁的小号","太神了","震撼","すき","可爱","上瘾","上头","洗脑","草","我浪","神","顶"]
target_bad_key_words = ["加油","注意","建议","进步","稚嫩","不足","不好",
                        "文艺复兴","倒退","大势所趋","dssq","烂"]

# 改动这个筛选条件之后，需要先把 AutoData/这次的数据/comment_data/ 和 AutoData/这次的数据/invalid_aid.pkl 删掉
tag_whitelist = ['音MAD']
tag_whitezone = [26]
whitelist_filter = lambda video_info, tags: (video_info['tid'] in tag_whitezone) or (len(set(tags).intersection(tag_whitelist))>0)

if not os.path.exists(base_path): os.makedirs(base_path)
str_time = datetime.datetime.strptime(str_time,"%y%m%d")
src_time = str_time + datetime.timedelta(days=-delta_days)
dst_time = src_time + datetime.timedelta(days=range_days)
logging.info(f"选取日期 从 {src_time.strftime('%y/%m/%d-%H:%m')} 到 {dst_time.strftime('%y/%m/%d-%H:%m')}")
data_folder_name = src_time.strftime("%y%m%d") + "-" + dst_time.strftime("%y%m%d")
data_path = os.path.join(base_path, data_folder_name)
if not os.path.exists(data_path): os.makedirs(data_path)

all_video_info: Dict[int, Dict] = {}
for video_zone in video_zones:
    logging.info(f"正在获取分区 {video_zone} 的视频信息")
    all_video_info_in_subzone = retrieve_video_info(src_time.timestamp(), dst_time.timestamp(), data_path, video_zone)
    logging.info(f"分区 {video_zone} 的视频信息获取完成，本分区视频总数: {len(all_video_info_in_subzone)}")
    all_video_info.update(all_video_info_in_subzone)
# for video_info in all_video_info.values():
#     video_pubtime   = datetime.datetime.fromtimestamp(video_info['pubdate'])
#     video_aid       = video_info['aid']
#     video_title     = video_info['title']
#     video_copyright = video_info['copyright']
#     video_zone      = video_info['tid']
#     print(f"视频 av 号: {video_aid}, 发布时间: {video_pubtime}, 标题: {video_title}, 版权: {video_copyright}, 视频分区: {video_zone}")
logging.info(f"视频信息获取完成，视频总数: {len(all_video_info)}")

skipped_aid, invalid_aid = retrieve_video_comment(data_path, all_video_info, whitelist_filter, sleep_inteval=1)
if len(skipped_aid)>0: logging.warning("被跳过的 aid: " + str(skipped_aid))
if len(invalid_aid)>0: logging.info("无效或被过滤的 aid: " + str(invalid_aid))
marshal.dump(invalid_aid, open(os.path.join(data_path, "invalid_aid.pkl"), "wb"))

logging.info("汇总评论中")
all_mid_list: Dict[int, Dict[str, Any]] = marshal.load(open(os.path.join(base_path, "all_mid_list.dat"), "rb"))
mid_s2_list = [mid_info['s2'] for mid_info in all_mid_list.values()]
# all_mid_s2_mean = sum(mid_s2_list) / len(mid_s2_list)
all_mid_s2_median = calc_median(mid_s2_list)
# for mid in sorted(all_mid_list.values(), key=lambda x: -x['s1']):
#     if mid['s1']>10: print("s1 = %7.2f, s2 = %4.2f, mid=%10i, name = %s" % (mid['s1'], mid['s2'], mid['mid'], mid['name'],))

aid_to_comment: Dict[int, List[Dict]] = defaultdict(list)
aid_to_tag: Dict[int, List[str]] = defaultdict(list)
for aid in all_video_info.keys():
    comment_file_path = os.path.join(data_path, "comment_data", f"{aid}.json")
    if not (os.path.exists(comment_file_path) or aid in invalid_aid or all_video_info[aid]['copyright']!=1):
        logging.warning(f"comment file {comment_file_path} not found")
        _, invalid_aid = retrieve_video_comment(data_path, all_video_info, sleep_inteval=1)
        if not os.path.exists(comment_file_path) or aid in invalid_aid: continue
    if aid not in invalid_aid and all_video_info[aid]['copyright'] == 1:
        with open(comment_file_path, "r", encoding="utf-8") as f:
            comment_data = json.load(f)
            if 'comment' not in comment_data: continue
            aid_to_tag[aid] = comment_data['tag']
            aid_to_comment[aid] = comment_data['comment']

logging.info("计算视频得分")
aid_to_score: Dict[int, float] = {}
aid_to_score_norm: Dict[int, float] = {}
for video_info in all_video_info.values():
    video_aid = video_info["aid"]
    video_score, video_score_norm = calc_aid_score(
        video_info, aid_to_comment[video_aid],
        target_good_key_words, target_bad_key_words,
        all_mid_list, s2_base=all_mid_s2_median)
    aid_to_score[video_aid] = video_score
    aid_to_score_norm[video_aid] = video_score_norm
logging.info("计分完成")

# aid_and_score: List[Tuple[int, float]] = []
# for aid in aid_to_score:
#     video_info   = all_video_info[aid]
#     aid_score, aid_score_norm = calc_aid_score(video_info, aid_to_comment[aid], target_good_key_words, target_bad_key_words, all_mid_list, s2_base=all_mid_s2_median)
#     if video_info["copyright"]==1: aid_and_score.append((aid, aid_score_norm))
# aid_and_score.sort(key=lambda x: -x[1])
# for aid, aid_score in aid_and_score[:100]: # 排名前100的视频
#     # print_aid_info(aid, verbose=False)
#     video_info = all_video_info[aid]
#     aid_author     = video_info["owner"]["name"]
#     aiu_mid        = video_info["owner"]["mid"]
#     aid_view       = video_info['stat']['view']
#     aid_title      = video_info['title']
#     aid_favorite   = video_info['stat']['favorite']
#     aid_view       = aid_view if aid_view >= 0 else 0
#     aid_comment    = aid_to_comment[aid]
#     _, aid_score_norm = calc_aid_score(video_info, aid_comment, target_good_key_words, target_bad_key_words, all_mid_list)
#     aid_pubtime = datetime.datetime.fromtimestamp(video_info["pubdate"]).strftime("%y%m%d-%H%M%S")
#     print("[av %i] 计分 = %5.6f @%s, 播放 %6i, 收藏 %5i, 评论 %3i || [uid %10i] %s: %s" % (aid, aid_score_norm, aid_pubtime, aid_view, aid_favorite, len(aid_comment), aiu_mid, aid_author, aid_title))

"""
>>> print(all_video_info[943387336])
{'aid': 943387336,
    'videos': 1,
    'tid': 26,
    'tname': 1664808239.21716,
    'copyright': 1,
    'pic': 'http://i0.hdslb.com/bfs/archive/9164a49a07f606cb1505f02f8bd2df2da150dadd.jpg',
    'title': '鸡摇滚 / エゴロック',
    'pubdate': 1664035208,
    'ctime': 1664035208,
    'desc': '不要这个时候打鸣，我还想多睡一会儿。\n\n本家：エゴロック - すりぃ （BV1jQ4y1a7JV）\n素材：鸡、雞、鷄、鷄、雞、鶏、鳮',
    'duration': 64,
    'mission_id': 870359,
    'owner': {'mid': 6636705, 'name': '坏枪'},
    'stat': {'view': 17787,
        'danmaku': 56,
        'reply': 151,
        'favorite': 788,
        'coin': 478,
        'share': 396,
        'his_rank': 0,
        'like': 2004,
        'dislike': 0},
    'dynamic': '',
    'cid': 842485570,
    'dimension': {'width': 1920, 'height': 1080, 'rotate': 0},
    'first_frame': 'http://i2.hdslb.com/bfs/storyff/n220924a21m4of3n077zbpaqu7eh2p5x_firsti.jpg',
    'pub_location': '重庆',
    'bvid': 'BV1rW4y1v7YJ',
    'season_type': 0}
    
>>> print(aid_to_score_norm[943387336])
2.185153921295668

>>> print(aid_to_tag[943387336])
['鬼畜', '音MAD', '打鸣', '鸡', 'すりぃ', 'エゴロック', '自我摇滚', '鬼畜星探企划']
"""