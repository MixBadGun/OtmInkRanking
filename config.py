import time
import os
import threading

if os.path.exists("./custom/time.txt"):
    usedTime = str(open("./custom/time.txt","r").read())
else:
    usedTime = time.strftime("%Y%m%d", time.localtime())
    with open("./custom/time.txt","w") as f:
        f.write(usedTime)

main_max_title = 30
side_max_title = 23
pick_max_reason = 40
sep_time = 20 # 间隔时间
main_end = 15 # 主榜个数
side_end = 40 # 副榜个数
side_count = 4 # 副榜显示
staticFormat = ["png","jpg","jpeg"]
delta_days = 11 # 以今天往前的第 delta_days 日开始统计
range_days = 7 # 统计 range_days 天的数据
screenRatio = 16 / 9

main_to_side_offset = -1

render_format = {
    "vcodec": "h264_nvenc", # 若没有 CUDA 加速，请切换为其它编码器或直接注释本行。
    "video_bitrate" : "10000k",
    "audio_bitrate" : "320k"
}
all_render_format = {
    "vcodec": "h264_nvenc", # 若没有 CUDA 加速，请切换为其它编码器或直接注释本行。
    "video_bitrate" : "10000k",
    "audio_bitrate" : "320k"
}
read_format = {
    "vcodec": "h264_cuvid" # 若没有 CUDA 加速，请切换为其它编码器或直接注释本行。
}
muitl_limit = threading.Semaphore(3)