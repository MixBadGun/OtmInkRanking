from pickup import pickData
from pick_create import PickVideo
import danmuku_time
import get_video

sep_time = 20 # 间隔时间

pickArr = pickData()

# PICK UP 合成
picks = 0

for picking in pickArr:
    picks += 1
    aid = picking[0]
    bvid = picking[1]
    cid = picking[2]
    full_time = picking[7]
    start_time = danmuku_time.danmuku_time(aid,cid,full_time,sep_time)
    get_video.get_video(aid,bvid,cid)
    PickVideo(aid,start_time,sep_time,picks)