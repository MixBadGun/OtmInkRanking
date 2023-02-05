import ffmpeg
from config import *

def SideVideo(main_end,side_end,side_count):
    sideBGM = ffmpeg.input("./custom/ed.mp4")
    sideBGMVideo = sideBGM.video
    sideBGMAudio = sideBGM.audio
    sideDuration = float(ffmpeg.probe("./custom/ed.mp4")["streams"][0]["duration"])
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
    ffmpeg.output(sideVideo,sideBGMAudio,"./output_clips/SideRank.mp4",**render_format).run()
SideVideo(15,40,4)