from moviepy.editor import *
import os
import shutil
import ffmpeg
import csv
from config import *

def duration(file,offset):
    return float(ffmpeg.probe(file)["streams"][0]["duration"]) + offset

def ffVideo(file):
    vi = ffmpeg.input(file,**read_format)
    viv = vi.video
    aud = vi.audio
    return [viv,aud]

def inVideo(file):
    name = file.split("/")[-1]
    vi = ffmpeg.input(file,**read_format)
    viv = vi.filter("fade",st=0,d=0.5)
    if not os.path.exists(f"./output_clips/temp/{name}"):
        ffmpeg.output(viv,f"./output_clips/temp/{name}",**render_format).run()
    viw = ffmpeg.input(f"./output_clips/temp/{name}",**read_format)
    aud = vi.audio
    return [viw,aud]

def inoutVideo(file):
    name = file.split("/")[-1]
    vi = ffmpeg.input(file,**read_format)
    viv = vi.filter("fade",st=0,d=0.5)
    viv = viv.filter("fade",t="out",st=duration(file,-0.5),d=0.5)
    if not os.path.exists(f"./output_clips/temp/{name}"):
        ffmpeg.output(viv,f"./output_clips/temp/{name}",**render_format).run()
    viw = ffmpeg.input(f"./output_clips/temp/{name}",**read_format)
    aud = vi.audio
    return [viw,aud]

def outVideo(file):
    name = file.split("/")[-1]
    vi = ffmpeg.input(file,**read_format)
    viv = vi.filter("fade",t="out",st=duration(file,-0.5),d=0.5)
    if not os.path.exists(f"./output_clips/temp/{name}"):
        ffmpeg.output(viv,f"./output_clips/temp/{name}",**render_format).run()
    viw = ffmpeg.input(f"./output_clips/temp/{name}",**read_format)
    aud = vi.audio
    return [viw,aud]

def AllVideo(main_end,pickArr,usedTime):
    with open("./custom/data.csv", "r", encoding="utf-8-sig") as csvfile:
        reader = csv.reader(csvfile)
        main_rank_column = [row[0] for row in reader]
    AllArr = []
    trueFiles = []
    for curDir, dirs, files in os.walk("./custom/ads"):
        for ads in files:
            AllArr.append(inoutVideo(f"./custom/ads/{ads}"))
            trueFiles.append(ads)
    if len(trueFiles) > 0:
        AllArr.append(inoutVideo("./output_clips/Opening.mp4"))
    else:
        AllArr.append(ffVideo("./output_clips/Opening.mp4"))
    filePath = f"./output_clips/{usedTime}"
    tempPath = f"./output_clips/temp"
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    if not os.path.exists(tempPath):
        os.mkdir(tempPath)
    AllArr.append(ffVideo("./template/pass/passMain.mp4"))

    for clips in range(main_end,insert_count+1,-1):
        rank_src = main_rank_column[clips]
        AllArr.append(ffVideo(f"./output_clips/MainRank_{rank_src}.mp4"))
        AllArr.append(ffVideo("./template/pass/pass.mp4"))
    rank_src = main_rank_column[insert_count+1]
    AllArr.append(ffVideo(f"./output_clips/MainRank_{rank_src}.mp4"))

    # Pick Up

    if pickArr != []:
        AllArr.append(ffVideo("./template/pass/passPick.mp4"))
        for clipsto in range(1,len(pickArr)):
            AllArr.append(ffVideo(f"./output_clips/PickRank_{clipsto}.mp4"))
            AllArr.append(ffVideo("./template/pass/pass.mp4"))
    if os.path.exists("./custom/canbin.mp4"):
        if len(pickArr) != 0:
            AllArr.append(outVideo(f"./output_clips/PickRank_{len(pickArr)}.mp4"))
        else:
            # AllArr[-1] = ffmpeg.filter(AllArr[-1],"fade",t="out",st="d-0.5",d=0.5,alpha=1)
            pass
        AllArr.append(inoutVideo("./template/pass/passCanbin.mp4"))
        AllArr.append(inoutVideo("./custom/canbin.mp4"))
        AllArr.append(inVideo("./template/pass/passMain.mp4"))
    else:
        if pickArr != []:
            AllArr.append(ffVideo(f"./output_clips/PickRank_{len(pickArr)}.mp4"))
            AllArr.append(ffVideo("./template/pass/passMain.mp4"))
        else:
            AllArr.append(ffVideo("./template/pass/pass.mp4"))

    # 倒数主榜

    for clips in range(insert_count,1,-1):
        rank_src = main_rank_column[clips]
        AllArr.append(ffVideo(f"./output_clips/MainRank_{rank_src}.mp4"))
        AllArr.append(ffVideo("./template/pass/pass.mp4"))
    rank_src = main_rank_column[1]

    if os.path.exists("./custom/ed.mp4"):
        AllArr.append(ffVideo(f"./output_clips/MainRank_{rank_src}.mp4"))
        AllArr.append(ffVideo("./template/pass/passSide.mp4"))
        if end_logo:
            AllArr.append(outVideo("./output_clips/SideRank.mp4"))
            AllArr.append(inVideo("./custom/end_logo.mp4"))
        else:
            AllArr.append(ffVideo("./output_clips/SideRank.mp4"))
    else:
        if end_logo:
            AllArr.append(outVideo(f"./output_clips/MainRank_{rank_src}.mp4"))
            AllArr.append(inVideo("./custom/end_logo.mp4"))
        else:
            AllArr.append(ffVideo(f"./output_clips/MainRank_{rank_src}.mp4"))

    onum = 0
    for items in AllArr:
        onum += 1
        if onum == 1:
            combVideo = items
            continue
        combVideo = ffmpeg.concat(combVideo[0],combVideo[1],items[0],items[1],v=1,a=1).node
    ffmpeg.output(combVideo[0],combVideo[1],f'./output_all/Rank_{usedTime}.mp4',**all_render_format).run()
    if os.path.exists("./custom/canbin.mp4"):
        shutil.move("./custom/canbin.mp4",f"{filePath}/canbin_{usedTime}.mp4")
    shutil.move("./output_clips/Opening.mp4",f"{filePath}/Opening.mp4")
    for clips in range(main_end,0,-1):
        rank_src = main_rank_column[clips]
        shutil.move(f"./output_clips/MainRank_{rank_src}.mp4",f"{filePath}/MainRank_{rank_src}.mp4")
    for clipsto in range(1,len(pickArr)+1):
        shutil.move(f"./output_clips/PickRank_{clipsto}.mp4",f"{filePath}/PickRank_{clipsto}.mp4")
    if os.path.exists("./custom/ed.mp4"):
        shutil.move("./output_clips/SideRank.mp4",f"{filePath}/SideRank.mp4")
        os.remove("./custom/ed.mp4")
    for curDir, dirs, files in os.walk("./output_clips/temp"):
        for temp_f in files:
            os.remove(f"./output_clips/temp/{temp_f}")
    os.remove("./custom/time.txt")