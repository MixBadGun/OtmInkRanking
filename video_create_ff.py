from config import *
import ffmpeg

def MainVideo(aid,start_time,sep_time,ranking):
    # 获取模板文件

    mainStart = ffmpeg.input("./template/main/back_come.mp4",vcodec="h264_cuvid")
    mainEnd = ffmpeg.input("./template/main/back_out.mp4",vcodec="h264_cuvid")
    mainDuration = float(ffmpeg.probe("./template/main/back_come.mp4")["streams"][0]["duration"]) + float(ffmpeg.probe("./template/main/back_out.mp4")["streams"][0]["duration"])
    mainDuring = ffmpeg.input("./template/main/back.png",t=sep_time - mainDuration,loop=1,framerate=60)
    main_back = ffmpeg.concat(mainStart,mainDuring,mainEnd)
    mainMaskStart = ffmpeg.input("./template/main/vid_mask_come.mp4",vcodec="h264_cuvid")
    mainMaskDuring = ffmpeg.input("./template/main/vid_mask.png",t=sep_time - mainDuration,loop=1,framerate=60)
    mainMaskEnd = ffmpeg.input("./template/main/vid_mask_out.mp4",vcodec="h264_cuvid")
    main_mask = ffmpeg.concat(mainMaskStart,mainMaskDuring,mainMaskEnd)

    # 获取视频文件

    coverImage = ffmpeg.input(f"./custom/output_image/main/MainRank_{ranking}.png",t=sep_time,loop=1,framerate=60)
    coverImage = ffmpeg.filter(coverImage,"fade",st=0.75,d=0.25,alpha=1)
    coverImage = ffmpeg.filter(coverImage,"fade",t="out",st=sep_time-0.5,d=0.5,alpha=1)
    videoSource = ffmpeg.input(f"./video/{aid}.mp4",ss=start_time,t=sep_time)
    backImage = ffmpeg.input("./template/main/back_inner.png",t=sep_time,loop=1,framerate=60)
    videoSourceAudio = ffmpeg.filter(videoSource.audio,"afade",t="in",d=1)
    videoSourceAudio = ffmpeg.filter(videoSourceAudio,"afade",t="out",st=sep_time-1,d=1)
    usingVideoSource = ffmpeg.filter(videoSource.video,"framerate",fps=60)
    usingVideoSource = ffmpeg.filter(usingVideoSource,"scale",w=-1,h=720)
    usingVideoSourceScaled = ffmpeg.filter([backImage,usingVideoSource],"overlay",x="82+1280/2-w/2",y=57)
    usingVideoSourceMasked = ffmpeg.filter([usingVideoSourceScaled,main_mask],"alphamerge")

    combinationVideo = ffmpeg.filter([main_back,usingVideoSourceMasked],"overlay")
    combinationVideo = ffmpeg.filter([combinationVideo,coverImage],"overlay")
    ffmpeg.output(combinationVideo,videoSourceAudio,'./output_clips/MainRank_'+str(ranking)+".mp4",vcodec="h264_nvenc",video_bitrate="10000k",audio_bitrate="320k").run()

    muitl_limit.release()