import ffmpeg
import datetime
from config import *

DisplayFont = './fonts/HarmonyOS_Sans_SC_Medium.ttf'

def OpeningVideo(usedTime):
    OpeningBack = ffmpeg.input("./template/opening/Opening.mp4")
    vi = OpeningBack.video
    au = OpeningBack.audio
    str_time = usedTime
    str_time = datetime.datetime.strptime(str_time,"%Y%m%d")
    src_time = str_time + datetime.timedelta(days=-delta_days)
    dst_time = src_time + datetime.timedelta(days=range_days) # 7天
    timeText = src_time.strftime('%Y/%m/%d') + " - " + dst_time.strftime('%Y/%m/%d')
    vi = ffmpeg.filter(vi,"drawtext",fontfile=DisplayFont,text=timeText,fontsize=48,fontcolor='white',x="1784-text_w",y=748,enable='between(t,12.12,17.12)')
    ffmpeg.output(vi,au,"./output_clips/Opening.mp4",**render_format).run()