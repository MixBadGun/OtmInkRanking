import json
import time
import os
from typing import List,Tuple,Dict,Union,Optional,Any,Set,Callable
from functools import partial
import random
import marshal
import datetime
import logging
import math
import requests
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s@%(funcName)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

# pip install bilibili_api_python
from bilibili_api import comment, sync, video
from bilibili_api import Credential
from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.exceptions.NetworkException import NetworkException
from aiohttp.client_exceptions import ServerDisconnectedError, ClientOSError

def calc_median(data: List[float]) -> float:
    data_ = sorted(data)
    half = len(data) // 2
    return (data_[half] + data_[~half]) / 2

def get_page_count(video_zone: int) -> int:
    headers = {
        'Accept': '*/*',
        # 'Cookie': raw_cookie,
        'Referer': 'https://www.bilibili.com/v/kichiku/mad/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.0'
    }
    # ↓只在子分区有效，比如音 MAD 区
    url = f"http://api.bilibili.com/x/web-interface/newlist?rid={video_zone}&type=0&pn=1&ps=1"
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    result = json.loads(response.text)
    if result["code"] == 0:
        return result["data"]["page"]["count"]
    return -1

def get_info_by_time(page_index: int, video_zone: int, time_from: str, time_to: str, ps=50, copyright="-1"):
    """
    :param time_from: 起始日期, 格式: yyyymmdd, 如: 20230701, 指此日期的 00:00 为始
    :param time_to: 结束日期, 格式: yyyymmdd, 如: 20230701, 指此日期的 23:59 为止
    :param ps: 每页视频数量，太大易被 ban
    :param copyright: "1": 自制, "0": 转载, "-1": 不限制
    """
    headers = {
        'accept': '*/*',
        # 'Cookie': raw_cookie, # using cookie may lessen the prob that being blocked 
        'referer': 'https://www.bilibili.com/v/kichiku/mad/', # 我不知道在请求其他分区时，填上不正确的 referer 会有什么影响
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41'
    }
    url = f"https://api.bilibili.com/x/web-interface/newlist_rank?search_type=video&view_type=hot_rank&cate_id={video_zone}&page={page_index}&pagesize={ps}&time_from={time_from}&time_to={time_to}&copy_right={copyright}"
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    result = json.loads(response.text)
    return_code = result["code"]
    if return_code != 0:
        raise Exception(f"Api [newlist_rank] Error: {return_code}, {result['message']}")
    
    data = result["data"]
    video_list: List[Dict[str, Any]] = data["result"]
    for i, video in enumerate(video_list):
        video.pop("arcrank" , None)
        video.pop("is_pay"  , None)
        video.pop("type"    , None)
        video.pop("badgepay", None)
        video['get_time'] = int(datetime.datetime.now().timestamp())
        video['tid'] = video_zone
        video['tag'] = video['tag'].lower().split(",")
    num_results: int = data["numResults"]
    num_pages: int = data["numPages"]
    return video_list, num_pages

# comment 具体格式见 https://github.com/SocialSisterYi/bilibili-API-collect/tree/master/docs/comment
def reply_trimmer(comments: List[Dict]) -> List[Dict]:
    processed_comments = []
    for comment in comments:
        processed_comments.append({
            "rpid": comment["rpid"], "mid": comment["mid"], "uname": comment["member"]["uname"],  # 评论rpID, 发送者UID, 发送者暱稱
            "count": comment["count"], "rcount": comment["rcount"], "ctime": comment["ctime"],  # 回复条数, 回复条数, 发送时间
            "like": comment["like"], "message": comment["content"]["message"],
            "mentioned": [comment_mentioned_uid["mid"] for comment_mentioned_uid in comment["content"]["members"]],
            "up_like": comment['up_action']['like'],
            "replies": [{
                "rpid": replies["rpid"], "mid": replies["mid"], "uname": replies["member"]["uname"],  # 评论rpID, 发送者UID, 发送者暱稱
                "count": replies["count"], "rcount": replies["rcount"], "ctime": replies["ctime"],  # 回复条数, 回复条数, 发送时间
                "like": replies["like"], "message": replies["content"]["message"],
                "mentioned": [reply_mentioned_uid["mid"] for reply_mentioned_uid in replies["content"]["members"]],
                "up_like": replies['up_action']['like'],
            } for replies in comment["replies"]] if comment["replies"] is not None else []
        })
    return processed_comments

async def get_comments(aid: int, credential: Credential) -> List[Dict]:
    comments = []
    page = 1
    count = 0
    while True:
        c = await comment.get_comments(aid, comment.ResourceType.VIDEO, page, credential=credential)
        assert type(c) is dict
        if "replies" not in c or c['replies'] is None: break
        comments.extend(c['replies'])
        count += c['page']['size']
        page += 1
        if count >= c['page']['count']: break
        time.sleep(1)
    return reply_trimmer(comments)

def retrieve_video_comment(data_path:str, all_video_info: Dict[int, Dict], force_update=False, max_try_times=10, sleep_inteval=3) -> Tuple[Set[int], Set[int]]:
    from config_login import sessdata, bili_jct, buvid3, dedeuserid
    credential = Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)
    skipped_aid = set()
    invalid_aid_path = os.path.join(data_path, "invalid_aid.pkl")
    if os.path.exists(invalid_aid_path): invalid_aid = marshal.load(open(invalid_aid_path, "rb"))
    else: invalid_aid = set()
    comment_dir = os.path.join(data_path, "comment")
    
    for n, video_info in enumerate(all_video_info.values()):
        video_aid = video_info['id']
        comments_dir_by_date = os.path.join(comment_dir, video_info['pubdate'][:10])
        comment_file_path = os.path.join(comments_dir_by_date, f"{video_aid}.json")
        if not force_update and os.path.exists(comment_file_path): continue
        if video_aid in invalid_aid: continue
        
        status, comments = retrieve_single_video_comment(video_aid, credential=credential, max_try_times=max_try_times, sleep_inteval=sleep_inteval)
        if status <= 0:
            if status == -1: invalid_aid.add(video_aid)
            if status == -2: skipped_aid.add(video_aid)
            time.sleep(sleep_inteval)
            continue
        
        if not os.path.exists(comments_dir_by_date): os.makedirs(comments_dir_by_date)
        with open(comment_file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(comments, ensure_ascii=False, indent=4))
        if video_info["review"]>20*2 and len(comments)==20: 
            logging.warning(f"获取 av{video_aid} 评论数 {len(comments): 4} 过少，若此问题多次出现需考虑重新获取 Cookie；进度 {n+1: 4} / {len(all_video_info)}")
        else:
            logging.debug(f"获取 av{video_aid} 评论成功，计评论数{len(comments): 4}, 进度 {n+1: 4} / {len(all_video_info)}")
    
    if len(invalid_aid)>0: marshal.dump(invalid_aid, open(os.path.join(data_path, "invalid_aid.pkl"), "wb"))
    return skipped_aid, invalid_aid

def retrieve_video_stat(data_path:str, aid_list:List[int], force_update=False, max_try_times=10, sleep_inteval=3) -> Tuple[Set[int], Set[int], Dict[int, Dict]]:
    skipped_aid = set()
    invalid_aid_path = os.path.join(data_path, "invalid_aid.pkl")
    if os.path.exists(invalid_aid_path): invalid_aid = marshal.load(open(invalid_aid_path, "rb"))
    else: invalid_aid = set()
    stat_dir = os.path.join(data_path, "stat")
    
    selected_aid_stats: Dict[int, Dict] = {}
    for n, video_aid in enumerate(aid_list):
        stat_file_path = os.path.join(stat_dir, f"{video_aid}.json")
        if not force_update and os.path.exists(stat_file_path):
            selected_aid_stats[video_aid] = json.load(open(stat_file_path, "r", encoding="utf-8"))
            continue
        if video_aid in invalid_aid: continue
        
        status, stat = retrieve_single_video_stat(video_aid, max_try_times=max_try_times, sleep_inteval=sleep_inteval)
        if status <= 0:
            if status == -1: invalid_aid.add(video_aid)
            if status == -2: skipped_aid.add(video_aid)
            time.sleep(sleep_inteval)
            continue
        
        with open(stat_file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(stat, ensure_ascii=False, indent=4))
        selected_aid_stats[video_aid] = stat
        logging.debug(f"获取 av{video_aid} 信息成功，点赞{stat['like']:6}, 硬币{stat['coin']:4}，弹幕{stat['danmaku']:4}，版权 {stat['copyright']}; 进度 {n+1: 4} / {len(aid_list)}")
    
    if len(invalid_aid)>0: marshal.dump(invalid_aid, open(os.path.join(data_path, "invalid_aid.pkl"), "wb"))
    return skipped_aid, invalid_aid, selected_aid_stats

def calc_aid_score(video_info: Dict, comment_list: Optional[List[Dict]], good_key_words: List[str], bad_key_words: List[str], all_mid_list: Dict[int, Dict], s2_base:float=0, show_verbose=False) -> Tuple[float, float]:
    if comment_list is None or list(comment_list)==0: return 0, 0
    aid_score = 0
    for comment in comment_list:
        comment_mid   = comment["mid"]
        comment_name  = all_mid_list[comment["mid"]]['name'] if comment["mid"] in all_mid_list else "————"
        comment_s1    = all_mid_list[comment["mid"]]['s1'] if comment["mid"] in all_mid_list else 0
        comment_s2    = s2_base + (all_mid_list[comment["mid"]]['s2'] if comment["mid"] in all_mid_list else 0)
        comment_score = (math.atan(comment_s1) + math.atan(comment_s2)) / (math.pi*2)
        comment_msg   = comment["message"].lower().replace("\n", "\t")
        comment_time  = time.strftime("@%y%m%d/%H%M", time.localtime(comment['ctime']))
        
        hit_good_key_words = False
        for key_word in good_key_words:
            if key_word in comment_msg:
                hit_good_key_words = True
                break
        hit_bad_key_words = False
        for key_word in bad_key_words:
            if key_word in comment_msg:
                hit_bad_key_words = True
                break
        multiply_value = 1 * (2 if hit_good_key_words else 1) * (0.5 if hit_bad_key_words else 1)
        aid_score += comment_score * multiply_value
        if show_verbose: print("[%10s] %s ( %6.2f + %4.2f ) x%.2f %s: %s" % (comment_mid, comment_time, comment_s1, comment_s2, multiply_value, comment_name, comment_msg))
    aid_favorite = video_info['favorites']
    # aid_score /= math.log2(len(comment_list)+2)
    aid_score_norm = math.sqrt(aid_score * math.log10(aid_favorite/10+1))
    # 调高了->热门视频的排名更高，调低了->低播放量而圈子向的视频排名更高
    return aid_score, aid_score_norm

def print_aid_info(video_info:Dict[str, Any], comments:List[Dict],
                    good_key_words: List[str], bad_key_words: List[str], 
                    all_mid_list: Dict[int, Dict], verbose:bool=False):
    aid          = video_info["id"]
    aid_author   = video_info["author"]
    aiu_mid      = video_info["mid"]
    aid_view     = int(video_info['play'])
    aid_title    = video_info['title']
    aid_favorite = video_info['favorites']
    aid_pubtime  = video_info["pubdate"]
    aid_view     = aid_view if aid_view >= 0 else 0
    aid_score, aid_score_norm = calc_aid_score(video_info, comments, good_key_words, bad_key_words, all_mid_list, show_verbose=verbose)
    print("[av %i] 计分 = %5.6f @%s, 播放 %6i, 收藏 %5i, 评论 %3i || [uid %10i] %s: %s" % (aid, aid_score_norm, aid_pubtime, aid_view, aid_favorite, len(comments), aiu_mid, aid_author, aid_title))
    

def retrieve_single_video_tag(video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[str]]:
    task = video.Video(aid=video_aid).get_tags
    status, tags_raw = apply_bilibili_api(task, video_aid, max_try_times, sleep_inteval)
    # tags = [{'id':tag['tag_id'], 'name':tag['tag_name']} for tag in tags_raw]
    tags = [tag['tag_name'] for tag in tags_raw]
    return status, tags

def retrieve_single_video_comment(video_aid: int, credential: Credential, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[Dict]]:
    task = partial(get_comments, video_aid, credential)
    status, comments_raw = apply_bilibili_api(task, video_aid, max_try_times, sleep_inteval)
    return status, comments_raw

def retrieve_single_video_stat(video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, Dict[str, Any]]:
    task = video.Video(aid=video_aid).get_stat
    status, stat = apply_bilibili_api(task, video_aid, max_try_times, sleep_inteval)
    assert isinstance(stat, dict)
    return status, stat

def apply_bilibili_api(task: Callable, video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[Dict]]:
    try_times = 0
    contents: List[Dict] = []
    while try_times < max_try_times:
        try: 
            contents = sync(task())
            break
        except (ServerDisconnectedError, ClientOSError):
            try_times += 1
            if try_times == max_try_times: # 网络错误
                logging.warning(f"ServerDisconnectedError at {video_aid}, skipped")
                return -2, []
        except ResponseCodeException as e:
            if e.code in {12002, 12061}: # 大概是被删了或是移到别的分区了
                logging.warning(f"ResponseCodeException at {video_aid}, aborted")
                return -1, [] # Invalid
            else:
                logging.error(f"Unhandled ResponseCodeException: {e.code} at {video_aid}, skipped")
                return -2, []
        except NetworkException as e:
            if e.status in {412}: # 被 B 站 ban 了
                logging.warning(f"NetworkException 412 at {video_aid}, retrying {try_times} times")
                try_times += random.randint(0, 1)
                time.sleep(sleep_inteval * try_times * 2)
            else:
                logging.error(f"Unhandled NetworkException: {e.status} at {video_aid}, skipped")
                return -2, [] 
        except Exception as e:
            logging.error(f"Unhandled Exception: {type(e)} {e}")
            return -2, []
        finally:
            time.sleep(sleep_inteval * (try_times + 1))
    
    return 1, contents