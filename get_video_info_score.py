import json
import os
from typing import List, Tuple, Dict, Union, Any
import marshal
import datetime
import logging
from collections import defaultdict
from config import base_path, delta_days, range_days, pull_video_copyright, video_zones
from config import tag_whitelist, tag_whitezone, prefilter_comment_less_than, main_end, side_end
from config import pull_full_list_stat, sleep_inteval
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s@%(funcName)s: %(message)s')

from get_video_info_score_func import *

str_time = datetime.datetime.now().strftime('%y%m%d') # 今天日期

# 其实这些关键词的影响并不大
target_good_key_words = [
    "fuxi","复习","複習","fx","高技术","好听","好汀","好聽","喜欢","喜歡","支持","漂亮","舒服"
    "死了","厉害","厲害","最好","最高","最佳","订餐","sk","suki","suang","爽",
    "不错","不錯","牛逼","牛批","nb","！！！","神作","帅","帥","触","觸","强","強","棒","天才",
    "tql","wsl","yyds","永远的神","谁的小号","太神了","震撼","すき","可爱","上瘾","上头","洗脑","草","我浪","神","顶"]
target_bad_key_words = ["加油","注意","建议","进步","稚嫩","不足","不好",
                        "文艺复兴","倒退","大势所趋","dssq","烂"]

if not os.path.exists(base_path): os.makedirs(base_path)
str_date = datetime.datetime.strptime(str_time,"%y%m%d")
src_date = str_date + datetime.timedelta(days=-delta_days)
dst_date = src_date + datetime.timedelta(days=+range_days-1)
src_date_str = src_date.strftime("%Y%m%d")
dst_date_str = dst_date.strftime("%Y%m%d")
logging.info(f"选取时间 从 {src_date_str}-00:00 到 {dst_date_str}-23:59")
data_folder_name = src_date_str + " - " + dst_date_str
data_path = os.path.join(base_path, data_folder_name)
stat_dir = os.path.join(data_path, "stat")
info_dir = os.path.join(data_path, "info")
comment_dir = os.path.join(data_path, "comment")
os.makedirs(stat_dir, exist_ok=True)
os.makedirs(info_dir, exist_ok=True)
os.makedirs(comment_dir, exist_ok=True)

####################### 拉取数据 #########################
all_video_info: Dict[int, Dict] = {}
for video_zone in video_zones:
    video_info_collection_file_name = f"info_{video_zone}.json"
    video_info_collection_file_path = os.path.join(info_dir, video_info_collection_file_name)
    if os.path.exists(video_info_collection_file_path):
        logging.info(f"分区 {video_zone} 的视频信息已经存有文件，直接读取")
        with open(video_info_collection_file_path, "r", encoding="utf-8") as f:
            all_video_info.update(json.load(f))
        continue
    info_page, num_pages = get_info_by_time(1, video_zone, src_date_str, dst_date_str, copyright=str(pull_video_copyright))
    logging.info(f"分区 {video_zone} 的第 1 页完成，共 {num_pages} 页")
    all_video_info.update({i['id']:i for i in info_page})
    # 如果页数正向遍历，那么一旦有视频被删除，列表上之后的视频会向前挪动
    # 跨页挪动的视频就会被漏掉，所以反向遍历
    for page_index in range(num_pages, 1, -1):
        time.sleep(sleep_inteval + random.random())
        info_page, num_pages = get_info_by_time(page_index, video_zone, src_date_str, dst_date_str, copyright=str(pull_video_copyright))
        all_video_info.update({i['id']:i for i in info_page})
        logging.info(f"第 {page_index} 页完成")
    with open(video_info_collection_file_path, "w", encoding="utf-8") as f:
        json.dump(all_video_info, f, ensure_ascii=False, indent=4)
logging.info(f"视频信息获取完成，视频总数: {len(all_video_info)}")

whitelist_filter = lambda video_info: (video_info['tid'] in tag_whitezone) or (len(set(video_info["tag"]).intersection(tag_whitelist))>0)
all_video_info = {int(k):v for k,v in all_video_info.items() if whitelist_filter(v)}
logging.info("按白名单过滤后，待拉取视频数: " + str(len(all_video_info)))
comment_count_filter = lambda video_info: (video_info["review"] > prefilter_comment_less_than)
all_video_info = {k:v for k,v in all_video_info.items() if comment_count_filter(v)}
logging.info("按评论数过滤后，待拉取视频数: " + str(len(all_video_info)))

skipped_aid, invalid_aid = retrieve_video_comment(data_path, all_video_info, force_update=False, sleep_inteval=sleep_inteval)
if len(skipped_aid)>0:
    logging.warning("被跳过的 aid: " + str(skipped_aid))
if len(invalid_aid)>0:
    logging.info("无效的 aid: " + str(invalid_aid))
    marshal.dump(invalid_aid, open(os.path.join(data_path, "invalid_aid.pkl"), "wb"))


####################### 计算得分 #########################
logging.info("汇总评论中")
all_mid_list: Dict[int, Dict[str, Any]] = marshal.load(open(os.path.join(base_path, "all_mid_list.dat"), "rb"))
mid_s2_list = [mid_info['s2'] for mid_info in all_mid_list.values()]
# all_mid_s2_mean = sum(mid_s2_list) / len(mid_s2_list)
all_mid_s2_median = calc_median(mid_s2_list)
# for mid in sorted(all_mid_list.values(), key=lambda x: -x['s1']):
#     if mid['s1']>10: print("s1 = %7.2f, s2 = %4.2f, mid=%10i, name = %s" % (mid['s1'], mid['s2'], mid['mid'], mid['name'],))

assert isinstance(invalid_aid, set)
aid_to_comment: Dict[int, List[Dict]] = defaultdict(list)
for aid, video_info in all_video_info.items():
    comment_file_path = os.path.join(comment_dir, video_info['pubdate'][:10], f"{aid}.json")
    if not (os.path.exists(comment_file_path) or aid in invalid_aid):
        logging.warning(f"comment file {comment_file_path} not found")
        _, invalid_aid = retrieve_video_comment(data_path, all_video_info, force_update=False, sleep_inteval=sleep_inteval)
        if not os.path.exists(comment_file_path) or aid in invalid_aid: continue
    if aid not in invalid_aid:
        with open(comment_file_path, "r", encoding="utf-8") as f:
            aid_to_comment[aid] = json.load(f)

logging.info("计算视频得分")
aid_to_score: Dict[int, float] = {}
aid_to_score_norm: Dict[int, float] = {}
for video_info in all_video_info.values():
    video_aid = video_info["id"]
    _, video_score_norm = calc_aid_score(
        video_info, aid_to_comment[video_aid],
        target_good_key_words, target_bad_key_words,
        all_mid_list, s2_base=all_mid_s2_median)
    aid_to_score_norm[video_aid] = video_score_norm
logging.info("计分完成")

aid_and_score: List[Tuple[int, float]] = [(k,v) for k,v in aid_to_score_norm.items()]
aid_and_score.sort(key=lambda x: -x[1])
if __name__ == "__main__":
    for aid, aid_score in aid_and_score[:main_end+side_end]:
        print_aid_info(all_video_info[aid], aid_to_comment[aid],
                        target_good_key_words, target_bad_key_words, all_mid_list, verbose=False)
pull_size = pull_full_list_stat and len(aid_and_score) or (main_end+side_end)
selected_aid = [aid for aid, _ in aid_and_score[:pull_size]]
logging.info(f"将获取排行前 {pull_size} 条视频的信息")
_, _, selected_video_stat = retrieve_video_stat(data_path, selected_aid, sleep_inteval=sleep_inteval)
logging.info(f"数据部分完成")


"""
* 各项意义见下 URL，实际稍有差别:
* https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/search/search_response.md
>>> print(all_video_info[615690406])
{
日期'pubdate': '2023-07-09 16:14:23',
封面'pic': '//i0.hdslb.com/bfs/archive/9af57aef1930c8808fc9440e960ada109a0a7a96.jpg',
    'tag': ['原曲不使用','迈克尔·杰克逊','ytpmv','michael\xa0jackson','ditizo','蚊的音mad征集令'],
时长'duration': 97,
av号'id': 615690406,
    'rank_score': 7189, # B 站自己展示用的排名，和我们的排名无关
    'senddate': 1688890463,
作者'author': '坏枪',
评论'review': 109,
    'mid': 6636705,
    'is_union_video': 0,
    'rank_index': 10,
播放'play': '7189',
    'rank_offset': 10,
简介'description': '嗷！\n\nBGM：Ditizo (Original) - The Guy Who Made（BV17r4y1n7wK）\n\n本作品参与了蚊的音MAD征集令 - 自由赛道',
弹幕'video_review': 9,
收藏'favorites': 431,
    'arcurl': 'http://www.bilibili.com/video/av615690406',
bv号'bvid': 'BV1Wh4y1E7RU',
标题'title': 'Ditizo!',
    'vt': 0,
    'enable_vt': 0
分区'tid': 26
    'get_time': 1689543449}

>>> print(selected_video_stat[615690406])
{   'aid': 615690406,
    'bvid': 'BV1Wh4y1E7RU',
    'view': 7419,
    'danmaku': 9,
    'reply': 109,
    'favorite': 437,
    'coin': 371,
    'share': 47,
    'like': 1190,
    'now_rank': 0,
    'his_rank': 0,
    'no_reprint': 1,
    'copyright': 1, 
    'argue_msg': '',
    'evaluation': '',
    'vt': None}

>>> print(aid_to_score_norm[315555174])
4.305885
"""