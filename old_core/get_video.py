import logging
import time
import requests

def get_video(aid,bvid,cid):
    # 声明变量

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36","referer": "https://www.bilibili.com/"}

    # 请求视频地址
    try:
        vid_origin = requests.get(url="https://api.bilibili.com/x/player/playurl?cid="+str(cid)+"&bvid="+str(bvid)+"&qn=64", headers=headers).json()
        vid_url = vid_origin["data"]["durl"][0]["url"]
    except:
        logging.error('获取 av' + str(aid) + ' 视频地址失败')
        exit()
    logging.info('获取 av' + str(aid) + ' 视频地址为 ' + vid_url)
    def download_vid():
        logging.info('下载 av' + str(aid) + ' 的视频中...')
        vid_content = requests.get(url=vid_url, headers=headers).content
        with open("video/"+ str(aid) + ".flv", "wb") as f:
            f.write(vid_content)
        logging.info('下载 av' + str(aid) + ' 的视频完成')
    vid_times = 0
    while(True):
        vid_times += 1
        logging.info('进行 av' + str(aid) + ' 的第 '+ str(vid_times) +' 次下载')
        try:
            download_vid()
            break
        except:
            logging.error('下载 av' + str(aid) + ' 的视频失败')