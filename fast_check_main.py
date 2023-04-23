import csv
import codecs
import requests
import webbrowser
import tkinter
import datetime
import subprocess
import os
import shutil
from function import getVideo,turnAid



with open("./fast_check/source/pick_data.csv","r",encoding="utf-8-sig",newline='') as csvfile:
    listed = csv.DictReader(csvfile)
    min_time = datetime.datetime.today() + datetime.timedelta(days=-8)
    with open("./fast_check/source/pick.csv","w",encoding="utf-8-sig",newline='') as csvwrite:
        writefile = csv.writer(csvwrite)
        writefile.writerow(["aid","reason","picker","owner"])
        # PICK UP 获取
        for item in listed:
            time = item["提交时间（自动）"]
            realtime = datetime.datetime.strptime(time,"%Y/%m/%d %H:%M:%S")
            if realtime < min_time:
                continue
            aid = turnAid(str(item["推荐作品 av 号 / BV 号（必填）"]))
            picker = item["推荐人"]
            if picker == "":
                picker = "神秘人"
            owner = item["作品原作者（必填）"]
            if owner == "无须作答":
                owner = ""
            url = f"https://www.bilibili.com/video/av{aid}"
            webbrowser.open(url, new=0, autoraise=True)
            top = tkinter.Tk()
            def tickCommand(root):
                writefile.writerow([aid,text,picker,owner])
                root.destroy()
            def noCommand(root):
                root.destroy()
            text = item["推荐理由（必填）"]
            textShow = tkinter.Text()
            textShow.insert('1.0',f"{picker}\n\n{text}")
            textShow.pack()
            tickButton = tkinter.Button(text="选择",font=("HarmonyOS Sans SC",30),command = lambda: tickCommand(top))
            noButton = tkinter.Button(text="废弃",font=("HarmonyOS Sans SC",30),command = lambda: noCommand(top))
            tickButton.pack()
            noButton.pack()
            top.mainloop()
        # ED 获取
        top = tkinter.Tk()
        titleText = tkinter.Label(text="请输入 ED 作品号")
        titleText.pack()
        typeText = tkinter.Entry()
        typeText.pack()
        def overCommand(root):
            if typeText.get() != "":
                getVideo(turnAid(typeText.get()))
                shutil.move("./fast_check/ed.mp4","./custom/ed.mp4")
            root.destroy()
        yesButton = tkinter.Button(text="确定",font=("HarmonyOS Sans SC",10),command = lambda: overCommand(top))
        yesButton.pack()
        top.mainloop()
shutil.move("./fast_check/source/pick.csv","./custom/pick.csv")
os.system("python second_main.py")