import ffmpeg
from config import *

def PickVideo(aid,start_time,sep_time,picks):
    # 获取模板文件

    pickStart = ffmpeg.input("./template/pick/pick_come.mp4",**read_format)
    pickEnd = ffmpeg.input("./template/pick/pick_out.mp4",**read_format)
    pickDuration = float(ffmpeg.probe("./template/pick/pick_come.mp4")["streams"][0]["duration"]) + float(ffmpeg.probe("./template/pick/pick_out.mp4")["streams"][0]["duration"])
    pickDuring = ffmpeg.input("./template/pick/pick_back.png",t=sep_time - pickDuration,loop=1,framerate=60)
    pick_back = ffmpeg.concat(pickStart,pickDuring,pickEnd)
    pickMaskStart = ffmpeg.input("./template/pick/pick_mask_come.mp4",**read_format)
    pickMaskDuring = ffmpeg.input("./template/pick/pick_mask.png",t=sep_time - pickDuration,loop=1,framerate=60)
    pickMaskEnd = ffmpeg.input("./template/pick/pick_mask_out.mp4",**read_format)
    pick_mask = ffmpeg.concat(pickMaskStart,pickMaskDuring,pickMaskEnd)

    # 获取视频文件

    coverImage = ffmpeg.input(f"./custom/output_image/pick/PickRank_{picks}.png",t=sep_time,loop=1,framerate=60)
    coverImage = ffmpeg.filter(coverImage,"fade",st=0.75,d=0.25,alpha=1)
    coverImage = ffmpeg.filter(coverImage,"fade",t="out",st=sep_time-0.5,d=0.5,alpha=1)
    videoSource = ffmpeg.input(f"./video/{aid}.mp4",ss=start_time,t=sep_time)
    videoSourceSize = ffmpeg.probe(f"./video/{aid}.mp4")["streams"][0]
    videoRatio = videoSourceSize["width"] / videoSourceSize["height"]
    backImage = ffmpeg.input("./template/pick/pick_back.png",t=sep_time,loop=1,framerate=60)
    videoSourceAudio = ffmpeg.filter(videoSource.audio,"afade",t="in",d=1)
    videoSourceAudio = ffmpeg.filter(videoSourceAudio,"afade",t="out",st=sep_time-1,d=1)
    usingVideoSource = ffmpeg.filter(videoSource.video,"framerate",fps=60)
    if(videoRatio > screenRatio):
        usingVideoSource = ffmpeg.filter(usingVideoSource,"scale",w=1280,h=-1)
    else:
        usingVideoSource = ffmpeg.filter(usingVideoSource,"scale",w=-1,h=720)
    usingVideoSourceScaled = ffmpeg.filter([backImage,usingVideoSource],"overlay",x="557+1280/2-w/2",y="89+720/2-h/2")
    usingVideoSourceMasked = ffmpeg.filter([usingVideoSourceScaled,pick_mask],"alphamerge")

    combinationVideo = ffmpeg.filter([pick_back,usingVideoSourceMasked],"overlay")
    combinationVideo = ffmpeg.filter([combinationVideo,coverImage],"overlay")
    ffmpeg.output(combinationVideo,videoSourceAudio,f'./output_clips/PickRank_{picks}.mp4',**render_format).run()

    muitl_limit.release()