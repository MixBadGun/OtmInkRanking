import logging
from os import sep
from moviepy.editor import *
from config import *
# 变量声明

screensize = (1920,1080)

def MainVideo(aid,start_time,sep_time,ranking):
    # 获取模板文件

    mainStart = VideoFileClip("./template/main/back_come.mp4")
    mainDuring = ImageClip("./template/main/back.png").set_duration(sep_time - 2.13333)
    mainEnd = VideoFileClip("./template/main/back_out.mp4")
    main_back = concatenate_videoclips([mainStart,mainDuring,mainEnd]).resize(screensize)
    mainMaskStart = VideoFileClip("./template/main/vid_mask_come.mp4",has_mask=True).to_mask()
    mainMaskDuring = ImageClip("./template/main/vid_mask.png").set_duration(sep_time - 2.13333).to_mask()
    mainMaskEnd = VideoFileClip("./template/main/vid_mask_out.mp4",has_mask=True).to_mask()
    main_mask = concatenate_videoclips([mainMaskStart,mainMaskDuring,mainMaskEnd],ismask=True)

    # 获取视频文件

    coverImage = ImageClip("./output_image/main/MainRank_"+str(ranking)+".png")
    coverImage = coverImage.set_duration(sep_time - 0.5)
    coverImage = coverImage.crossfadein(0.5).crossfadeout(1.0)
    videoSource = VideoFileClip("./video/"+str(aid)+".mp4").fx(afx.audio_normalize)
    usingVideoSource = videoSource.subclip(start_time,start_time+sep_time)
    usingVideoSource = usingVideoSource.audio_fadein(1).audio_fadeout(1)
    usingVideoSource = usingVideoSource.resize(width=1280,height=720)
    usingVideoSource = usingVideoSource.set_pos((82+1280/2-usingVideoSource.w/2,57+720/2-usingVideoSource.h/2))
    usingVideoSourceMasked = CompositeVideoClip([usingVideoSource],size=screensize).set_mask(main_mask)

    combinationVideo = CompositeVideoClip([main_back,usingVideoSourceMasked,coverImage.set_start(0.5)])
    combinationVideo.write_videofile('./output_clips/MainRank_'+str(ranking)+".mp4")

    for l in [mainStart,mainDuring,mainEnd,main_back,mainMaskStart,mainMaskDuring,mainMaskEnd,main_mask,coverImage,videoSource,usingVideoSource,usingVideoSourceMasked,combinationVideo]:
        l.close()

    muitl_limit.release()