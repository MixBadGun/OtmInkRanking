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

# pip install bilibili_api_python
from bilibili_api import comment, sync, video
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

def get_info(page: int, video_zone: int, ps=20):
    headers = {
        'accept': '*/*',
        # 'Cookie': raw_cookie, # using cookie may lessen the prob that being blocked 
        'referer': 'https://www.bilibili.com/v/kichiku/mad/', # 我不知道请求不同的分区时，填上正确的 referer 会有什么影响
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41'
    }
    url = f"http://api.bilibili.com/x/web-interface/newlist?rid={video_zone}&type=0&pn={page}&ps={ps}" # OR USE HTTPS
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    result = json.loads(response.text)
    return_code = result["code"]
    return_message = result["message"]
    
    if return_code != 0:
        return [return_code, return_message], -1
    video_list: Dict[str, Any] = result["data"]["archives"]

    for i, video in enumerate(video_list):
        # video.pop('tid')
        video.pop('state')
        video.pop('rights')
        # video.pop("short_link")
        video.pop("short_link_v2")
        video.pop("is_ogv")
        video.pop("ogv_info")
        video.pop("rcmd_reason")
        video['tname'] = datetime.datetime.now().timestamp()
        video["owner"].pop('face')
        video["stat"].pop('aid')
        video["stat"].pop('now_rank')
    video_count: int = result["data"]["page"]["count"]
    # print(video_list[0:2])
    return video_list, video_count

def retrieve_video_info(src_timestamp: float, dst_timestamp: float, data_path: str, video_zone:int, sleep_inteval = 4) -> Dict[int, Dict]:
    video_info_file_name = "video_info_%i.pkl" % video_zone
    if os.path.exists(os.path.join(data_path, video_info_file_name)):
        with open(os.path.join(data_path, video_info_file_name), "rb") as f:
            all_video_info = marshal.load(f)
        return all_video_info
    all_video_info: Dict[int, Dict] = dict()
    
    # find the first page that contains the target video that published after `dst_timestamp`
    page_index = 2
    video_per_page:int = 25
    page_change_step = 1 # page step of searching which page the dst video in
    page_status_dict: Dict[int, bool] = dict()
    while True:
        if page_index not in page_status_dict:
            info_page, _ = get_info(page_index, video_zone, video_per_page)
            is_video_after_dst_time = [i['pubdate']>dst_timestamp for i in info_page]
            time.sleep(sleep_inteval)
        if (page_index in page_status_dict and page_status_dict[page_index]) or (page_index not in page_status_dict and all(is_video_after_dst_time)):
            page_status_dict[page_index] = True
            logging.info(f"第 {page_index} 页所有视频均发布于 {datetime.datetime.fromtimestamp(dst_timestamp)} 之後，其中最早的在 {datetime.datetime.fromtimestamp(info_page[-1]['pubdate'])}")
            page_change_step *= 2
            page_index += page_change_step
            continue
        elif (page_index in page_status_dict and not page_status_dict[page_index]) or (page_index not in page_status_dict and not any(is_video_after_dst_time)):
            page_status_dict[page_index] = False
            logging.info(f"第 {page_index} 页所有视频均发布于 {datetime.datetime.fromtimestamp(dst_timestamp)} 之前，其中最新的在 {datetime.datetime.fromtimestamp(info_page[0]['pubdate'])}")
            page_change_step = max(1, page_change_step//2)
            page_index -= page_change_step
            if page_change_step==1 and page_index in page_status_dict and page_status_dict[page_index]:
                break
            continue
        elif any(is_video_after_dst_time):
            break
    logging.info(f"从第 {page_index} 页开始统计")

    # retrieve info of the video that was published between `src_timestamp` and `dst_timestamp`
    video_count_before:int = 0 # get_page_count()
    while True:
        info_page, video_count_present = get_info(page_index, video_zone, video_per_page)
        if video_count_present == -1:
            logging.error(f"Error when getting video info, page: {page_index}")
            time.sleep(40)
        
        if video_count_present < video_count_before:
            logging.info(f"Video count changed from {video_count_before} to {video_count_present}")
            page_index = max(1, page_index-1)
            video_count_before = video_count_present
            time.sleep(sleep_inteval + random.random())
            continue
        
        video_count_before = video_count_present
        is_video_before_src_time = [i['pubdate']<src_timestamp for i in info_page]
        for video_info in info_page:
            if not (src_timestamp < video_info['pubdate'] < dst_timestamp):
                continue # video was not published in the target time range
            video_info_retrieve_time = video_info['tname']
            video_aid:int = video_info['aid']
            if video_aid not in all_video_info:
                all_video_info[video_aid] = video_info
            elif video_info_retrieve_time > all_video_info[video_aid]['tname']: # update video info
                all_video_info[video_aid] = video_info
        
        if any(is_video_before_src_time):
            logging.info(f"第 {page_index} 页有视频发布早于 {datetime.datetime.fromtimestamp(src_timestamp)}，任务结束")
            break
        logging.info(f"第 {page_index} 页完成，本页最新/最早的视频发布于 {datetime.datetime.fromtimestamp(info_page[0]['pubdate'])} / {datetime.datetime.fromtimestamp(info_page[-1]['pubdate'])}")
        page_index += 1
        time.sleep(sleep_inteval + random.random())
    marshal.dump(all_video_info, open(os.path.join(data_path, video_info_file_name), "wb"))
    return all_video_info

def reply_processer(comments: List[Dict]) -> List[Dict]:
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

async def get_comments(aid: int) -> List[Dict]:
    comments = []
    page = 1
    count = 0
    while True:
        c = await comment.get_comments(aid, comment.ResourceType.VIDEO, page)
        if "replies" not in c or c['replies'] is None: break
        comments.extend(c['replies'])
        count += c['page']['size']
        page += 1
        if count >= c['page']['count']: break
        time.sleep(1)
    return reply_processer(comments)

def retrieve_video_comment(data_path:str, all_video_info: Dict[int, Dict], whitelist_filter: Callable[[Dict, List[str]], bool], force_update=False, max_try_times=10, sleep_inteval=3) -> Tuple[Set[int], Set[int]]:
    skipped_aid = set()
    invalid_aid_path = os.path.join(data_path, "invalid_aid.pkl")
    if os.path.exists(invalid_aid_path): invalid_aid = marshal.load(open(invalid_aid_path, "rb"))
    else: invalid_aid = set()
    comment_data_folder = os.path.join(data_path, "comment_data")
    if not os.path.exists(comment_data_folder): os.makedirs(comment_data_folder)
    
    for n, video_info in enumerate(all_video_info.values()):
        video_aid = video_info['aid']
        
        if video_info['copyright'] != 1: continue # 只爬取原创视频
        video_comment_file_full_path = os.path.join(comment_data_folder, f"{video_aid}.json")
        if not force_update and os.path.exists(video_comment_file_full_path): continue
        if video_aid in invalid_aid: continue
                
        if video_info["stat"]["reply"] == 0:
            with open(video_comment_file_full_path, "w", encoding="utf-8") as f:
                f.write("{}")
            logging.debug(f"av{video_aid} 似乎无评论，已跳过，进度 {n+1: 4} / {len(all_video_info)}")
            continue
        
        status, tags = retrieve_single_video_tag(video_aid, max_try_times=max_try_times, sleep_inteval=sleep_inteval)
        if status <= 0:
            if status == -1: invalid_aid.add(video_aid)
            if status == -2: skipped_aid.add(video_aid)
            time.sleep(sleep_inteval)
            continue
        if not whitelist_filter(video_info, tags):
            with open(video_comment_file_full_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({"tag":tags}, ensure_ascii=False, indent=4))
            logging.debug(f"av{video_aid} 已被过滤，进度 {n+1: 4} / {len(all_video_info)}")
            invalid_aid.add(video_aid)
            continue
        
        status, comments = retrieve_single_video_comment(video_aid, max_try_times=max_try_times, sleep_inteval=sleep_inteval)
        if status <= 0:
            if status == -1: invalid_aid.add(video_aid)
            if status == -2: skipped_aid.add(video_aid)
            time.sleep(sleep_inteval)
            continue
        
        with open(video_comment_file_full_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"tag":tags, "comment":comments}, ensure_ascii=False, indent=4))
        logging.debug(f"获取 av{video_aid} 评论成功，计评论数{len(comments): 4}, 进度 {n+1: 4} / {len(all_video_info)}")
    
    if len(invalid_aid)>0: marshal.dump(invalid_aid, open(os.path.join(data_path, "invalid_aid.pkl"), "wb"))
    return skipped_aid, invalid_aid

def calc_aid_score(video_info: Dict, comment_list: Optional[List[Dict]], good_key_words: List[str], bad_key_words: List[str], all_mid_list: Dict[int, Dict], s2_base:int=0, show_verbose=False) -> Tuple[float, float]:
    if list(comment_list)==0: return 0, 0
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
    aid_favorite = video_info['stat']['favorite']
    # aid_score /= math.log2(len(comment_list)+2)
    aid_score_norm = math.sqrt(aid_score * math.log10(aid_favorite/10+1))
    # ↑100 above is a variable to adjust the weight of favorite count, lower means more focus on low-view video
    # 调高了->热门视频的排名更高，调低了->低播放量而圈子向的视频排名更高
    return aid_score, aid_score_norm

# def print_aid_info(aid:int, verbose:bool=False):
#     video_info   = all_video_info[aid]
#     aid_author   = video_info["owner"]["name"]
#     aiu_mid      = video_info["owner"]["mid"]
#     aid_view     = video_info['stat']['view']
#     aid_title    = video_info['title']
#     aid_favorite = video_info['stat']['favorite']
#     aid_view     = aid_view if aid_view >= 0 else 0
#     aid_comment  = aid_to_comment[aid]
#     aid_pubtime  = datetime.datetime.fromtimestamp(video_info["pubdate"]).strftime("%y%m%d-%H%M%S")
#     aid_score, aid_score_norm = calc_aid_score(video_info, aid_comment, target_good_key_words, target_bad_key_words, all_mid_list, show_verbose=verbose)
#     print("[av %i] (%7.3f -> %6.3f ) @%s, 播放 %6i, 收藏 %5i, 收藏 %3i || [uid %10i] %s: %s" % (aid, aid_score, aid_score_norm, aid_pubtime, aid_view, aid_favorite, len(aid_comment), aiu_mid, aid_author, aid_title))
    

def retrieve_single_video_tag(video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[str]]:
    task = video.Video(aid=video_aid).get_tags
    status, tags_raw = apply_bilibili_api(task, video_aid, max_try_times, sleep_inteval)
    # tags = [{'id':tag['tag_id'], 'name':tag['tag_name']} for tag in tags_raw]
    tags = [tag['tag_name'] for tag in tags_raw]
    return status, tags

def retrieve_single_video_comment(video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[Dict]]:
    task = partial(get_comments, video_aid)
    status, comments_raw = apply_bilibili_api(task, video_aid, max_try_times, sleep_inteval)
    return status, comments_raw

def apply_bilibili_api(task: Callable, video_aid: int, max_try_times=10, sleep_inteval=3) -> Tuple[int, List[Dict]]:
    try_times = 0
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