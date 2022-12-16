from moviepy.editor import *
import datetime

delta_days = 10
DisplayFont = './fonts/HarmonyOS_Sans_SC_Medium.ttf'

def OpeningVideo(usedTime):
    OpeningBack = VideoFileClip("./template/opening/OpeningShort.mp4")
    str_time = usedTime
    str_time = datetime.datetime.strptime(str_time,"%Y%m%d")
    src_time = str_time + datetime.timedelta(days=-delta_days)
    dst_time = src_time + datetime.timedelta(days=7) # 7天
    timeText = src_time.strftime('%Y/%m/%d') + " - " + dst_time.strftime('%Y/%m/%d')
    text = TextClip(timeText,fontsize=48,color='#FA7097',font=DisplayFont).set_duration(6.0)
    text = text.crossfadein(1.0).crossfadeout(1.0)
    text = text.set_pos((1784-text.w,748))
    outVideo = CompositeVideoClip([OpeningBack,text.set_start(5.6)])
    outVideo.write_videofile("./output_clips/Opening.mp4",fps=60)
    for l in [OpeningBack]:
        l.close()