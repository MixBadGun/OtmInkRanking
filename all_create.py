from moviepy.editor import *
import os
import shutil

# 变量声明

screensize = (1920,1080)
preventNoiseOffset = -0.07 # 防止结尾噪音

def VideoMusicOffset(video):
    music = video.audio
    return video.set_audio(music.subclip(0,preventNoiseOffset))

def AllVideo(main_end,pickArr,usedTime):
    AllArr = []
    for curDir, dirs, files in os.walk("./custom/ads"):
        trueFiles = []
        for ads in files:
            if ads[0:8] == usedTime:
                AllArr.append(VideoFileClip(f"./custom/ads/{ads}").fadein(0.5).fadeout(0.5))
                trueFiles.append(ads)
        if len(trueFiles) > 0:
            AllArr.append(VideoMusicOffset(VideoFileClip("./output_clips/Opening.mp4").fadein(0.5)))
        else:
            AllArr.append(VideoMusicOffset(VideoFileClip("./output_clips/Opening.mp4")))
    filePath = f"./output_clips/{usedTime}"
    os.mkdir(filePath)
    AllArr.append(VideoFileClip("./template/pass/passMain.mp4"))
    for clips in range(main_end,1,-1):
        AllArr.append(VideoMusicOffset(VideoFileClip(f"./output_clips/MainRank_{clips}.mp4")))
        AllArr.append(VideoFileClip("./template/pass/pass.mp4"))
    AllArr.append(VideoMusicOffset(VideoFileClip("./output_clips/MainRank_1.mp4")))
    if pickArr != []:
        AllArr.append(VideoFileClip("./template/pass/passPick.mp4"))
        for clipsto in range(1,len(pickArr)):
            AllArr.append(VideoMusicOffset(VideoFileClip(f"./output_clips/PickRank_{clipsto}.mp4")))
            AllArr.append(VideoFileClip("./template/pass/pass.mp4"))
    if os.path.exists("./custom/canbin.mp4"):
        if len(pickArr) != 0:
            AllArr.append(VideoMusicOffset(VideoFileClip(f"./output_clips/PickRank_{len(pickArr)}.mp4")).fadeout(0.5))
        else:
            AllArr[-1] = AllArr[-1].fadeout(0.5)
        AllArr.append(VideoFileClip("./template/pass/passCanbin.mp4").fadein(0.5).fadeout(0.5))
        AllArr.append(VideoFileClip("./custom/canbin.mp4").fadein(0.5).fadeout(0.5))
        AllArr.append(VideoFileClip("./template/pass/passSide.mp4").fadein(0.5))
    else:
        AllArr.append(VideoMusicOffset(VideoFileClip(f"./output_clips/PickRank_{len(pickArr)}.mp4")))
        AllArr.append(VideoFileClip("./template/pass/passSide.mp4"))
    AllArr.append(VideoFileClip("./output_clips/SideRank.mp4"))
    combVideo = concatenate_videoclips(AllArr)
    combVideo.write_videofile(f'./output_all/Rank_{usedTime}.mp4',fps=60,bitrate='10000k',audio_bitrate='3000k')
    for l in AllArr:
        l.close()
    if os.path.exists("./custom/canbin.mp4"):
        shutil.move("./custom/canbin.mp4",f"{filePath}/canbin_{usedTime}.mp4")
    shutil.move("./output_clips/Opening.mp4",f"{filePath}/Opening.mp4")
    for clips in range(main_end,0,-1):
        shutil.move(f"./output_clips/MainRank_{clips}.mp4",f"{filePath}/MainRank_{clips}.mp4")
    for clipsto in range(1,len(pickArr)+1):
        shutil.move(f"./output_clips/PickRank_{clipsto}.mp4",f"{filePath}/PickRank_{clipsto}.mp4")
    shutil.move("./output_clips/SideRank.mp4",f"{filePath}/SideRank.mp4")
    os.remove("./custom/time.txt")