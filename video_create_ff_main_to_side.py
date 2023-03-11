from config import *
import ffmpeg

def MainToSideVideo(aid,start_time,sep_time,ranking):
    # 获取模板文件

    mainStart = ffmpeg.input("./template/main/back_come.mp4",**read_format)
    mainDuration = float(ffmpeg.probe("./template/main/back_come.mp4")["streams"][0]["duration"])
    mainDuring = ffmpeg.input("./template/main/back.png",t=sep_time - mainDuration,loop=1,framerate=60)
    main_back = ffmpeg.concat(mainStart,mainDuring)
    mainMaskStart = ffmpeg.input("./template/main/vid_mask_come.mp4",**read_format)
    mainMaskDuring = ffmpeg.input("./template/main/vid_mask.png",t=sep_time - mainDuration,loop=1,framerate=60)
    main_mask = ffmpeg.concat(mainMaskStart,mainMaskDuring)

    # 获取视频文件

    coverImage = ffmpeg.input(f"./custom/output_image/main/MainRank_{ranking}.png",t=sep_time,loop=1,framerate=60)
    coverImage = ffmpeg.filter(coverImage,"fade",st=0.75,d=0.25,alpha=1)
    coverImage = ffmpeg.filter(coverImage,"fade",t="out",st=sep_time-0.5,d=0.5,alpha=1)
    videoSource = ffmpeg.input(f"./video/{aid}.mp4",ss=start_time,t=sep_time)
    videoSourceSize = ffmpeg.probe(f"./video/{aid}.mp4")["streams"][0]
    videoRatio = videoSourceSize["width"] / videoSourceSize["height"]
    backImage = ffmpeg.input("./template/main/back_inner.png",t=sep_time,loop=1,framerate=60)
    videoSourceAudio = ffmpeg.input(f"./video/{aid}.mp4",ss=start_time).audio
    usingVideoSource = ffmpeg.filter(videoSource.video,"framerate",fps=60)
    if(videoRatio > screenRatio):
        usingVideoSource = ffmpeg.filter(usingVideoSource,"scale",w=1280,h=-1)
    else:
        usingVideoSource = ffmpeg.filter(usingVideoSource,"scale",w=-1,h=720)
    usingVideoSourceScaled = ffmpeg.filter([backImage,usingVideoSource],"overlay",x="82+1280/2-w/2",y="57+720/2-h/2")
    usingVideoSourceMasked = ffmpeg.filter([usingVideoSourceScaled,main_mask],"alphamerge")

    combinationVideo = ffmpeg.filter([main_back,usingVideoSourceMasked],"overlay")
    combinationVideo = ffmpeg.filter([combinationVideo,coverImage],"overlay")

    sideBGM = ffmpeg.input(f"./video/{aid}.mp4",ss=start_time+sep_time)
    sideBGMVideo = sideBGM.video
    sideDuration = float(ffmpeg.probe(f"./video/{aid}.mp4")["streams"][0]["duration"]) - sep_time
    sideBGM = sideBGMVideo.filter("scale",w=-1,h=233)
    sideBack = ffmpeg.input("./template/side/side_back.png",t=sideDuration,loop=1,framerate=60)
    sideCover = ffmpeg.filter(sideBack,"crop",x="in_w-560",y="in_h-310",w=560,h=310)
    sideStaff = ffmpeg.input("./custom/staff.png",t=sideDuration,loop=1,framerate=60)
    sideDur = sideDuration / int(side_end / side_count)
    for fournum in range(main_end+1,main_end+side_end+1,side_count):
        sidePic = (ffmpeg.input(f"./custom/output_image/side/SideRank_{fournum}-{fournum+side_count-1}.png",t=sideDur,loop=1,framerate=60)
                   .filter("fade",t="in",d=0.25,alpha=1)
                   .filter("fade",t="out",st=sideDur-0.25,d=0.25,alpha=1)
                    )
        if fournum == main_end+1:
            sideAll = sidePic
            continue
        sideAll = ffmpeg.concat(sideAll,sidePic)
    sideVideo = ffmpeg.overlay(sideBack,sideStaff,x="1598-w/2",y=f"740-((h+740)/{sideDuration})*t")
    sideVideo = ffmpeg.overlay(sideVideo,sideCover,x="W-w",y="H-h")
    sideVideo = ffmpeg.overlay(sideVideo,sideBGM,x=1373,y=780)
    sideVideo = ffmpeg.overlay(sideVideo,sideAll)
    main_and_side = ffmpeg.concat(combinationVideo,sideVideo)

    main_to_side_during_back = ffmpeg.input("./template/main_to_side/passSide.mp4",itsoffset=sep_time+main_to_side_offset,**read_format)
    main_to_side_during_mask = ffmpeg.input("./template/main_to_side/passSide_mask.mp4",itsoffset=sep_time+main_to_side_offset,**read_format)
    main_to_side_during = ffmpeg.filter([main_to_side_during_back,main_to_side_during_mask],"alphamerge")

    main_and_side_all = ffmpeg.overlay(main_and_side,main_to_side_during,repeatlast=0)
    ffmpeg.output(main_and_side_all,videoSourceAudio,'./output_clips/MainRank_'+str(ranking)+".mp4",**render_format).run()