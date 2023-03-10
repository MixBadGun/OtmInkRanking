import logging
from os import sep
from moviepy.editor import *
from config import *
# 变量声明

screensize = (1920,1080)

def PickVideo(aid,start_time,sep_time,picks):
    # 获取模板文件

    pickStart = VideoFileClip("./template/pick/pick_come.mp4")
    pickEnd = VideoFileClip("./template/pick/pick_out.mp4")
    pickDuration = pickStart.duration + pickEnd.duration
    pickDuring = ImageClip("./template/pick/pick_back.png").set_duration(sep_time - pickDuration)
    pick_back = concatenate_videoclips([pickStart,pickDuring,pickEnd]).resize(screensize)
    pickMaskStart = VideoFileClip("./template/pick/pick_mask_come.mp4",has_mask=True).to_mask()
    pickMaskDuring = ImageClip("./template/pick/pick_mask.png").set_duration(sep_time - pickDuration).to_mask()
    pickMaskEnd = VideoFileClip("./template/pick/pick_mask_out.mp4",has_mask=True).to_mask()
    pick_mask = concatenate_videoclips([pickMaskStart,pickMaskDuring,pickMaskEnd],ismask=True)

    # 获取视频文件

    coverImage = ImageClip("./custom/output_image/pick/PickRank_"+str(picks)+".png")
    coverImage = coverImage.set_duration(sep_time - 0.75)
    coverImage = coverImage.crossfadein(0.25).crossfadeout(0.5)
    videoSource = VideoFileClip("./video/"+str(aid)+".mp4").fx(afx.audio_normalize)
    usingVideoSource = videoSource.subclip(start_time,start_time+sep_time)
    usingVideoSource = usingVideoSource.audio_fadein(1).audio_fadeout(1)
    usingVideoSource = usingVideoSource.resize(width=1280,height=720)
    usingVideoSource = usingVideoSource.set_pos((557+1280/2-usingVideoSource.w/2,89+720/2-usingVideoSource.h/2))
    usingVideoSourceMasked = CompositeVideoClip([usingVideoSource],size=screensize).set_mask(pick_mask)

    combinationVideo = CompositeVideoClip([pick_back,usingVideoSourceMasked,coverImage.set_start(0.75)])
    combinationVideo.write_videofile('./output_clips/PickRank_'+str(picks)+".mp4",fps=60,bitrate='10000k',audio_bitrate='3000k')

    for l in [pickStart,pickDuring,pickEnd,pick_back,pickMaskStart,pickMaskDuring,pickMaskEnd,pick_mask,coverImage,videoSource,usingVideoSource,usingVideoSourceMasked,combinationVideo]:
        l.close()
    muitl_limit.release()