from math import floor
from moviepy.editor import *
# 变量声明

screensize = (1920,1080)

def SideVideo(main_end,side_end,side_count):
    sideBGM = VideoFileClip("./custom/ed.mp4")
    sideBGM = sideBGM.set_position((1373,780))
    sideBGM = sideBGM.resize((415,233))
    sideBack = ImageClip("./template/side/side_back.png")
    sideStaff = ImageClip("./custom/staff.png")
    sideRollH = 730 + sideStaff.h
    sideK = sideRollH / sideBGM.duration
    def sideStaffRoll(t):
        ox = 1598 - sideStaff.w / 2
        oy = 730
        sideStaffPos = oy - t*sideK
        return (ox,sideStaffPos)
    sideStaff = sideStaff.set_position(sideStaffRoll)
    sideStaffOut = CompositeVideoClip([sideStaff],size=screensize).fx(vfx.crop,1363,0,1363+435,771).set_position((1363,0))
    sideDur = sideBGM.duration / int(side_end / side_count)
    sideArr = []
    for fournum in range(main_end+1,main_end+side_end+1,4):
        sidePic = ImageClip(f"./custom/output_image/side/SideRank_{fournum}-{fournum+side_count-1}.png").set_duration(sideDur)
        sidePic = sidePic.crossfadein(0.25).crossfadeout(0.25)
        sideArr.append(sidePic)
    sideAllPic = concatenate_videoclips(sideArr)
    sideVideo = CompositeVideoClip([sideBack,sideBGM,sideAllPic,sideStaffOut],size=screensize).set_duration(sideBGM.duration)
    sideVideo.write_videofile("./output_clips/SideRank.mp4",fps=60,bitrate='10000k',audio_bitrate='3000k')