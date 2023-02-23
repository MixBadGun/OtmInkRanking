import csv
import codecs
import requests
import webbrowser
import tkinter
import datetime
import subprocess
import os
import shutil

def getVideo(aid):
    subprocess.Popen(f'lux -c ./cookies/cookie.txt -o ./fast_check/ -O ed av{aid}').wait()

def turnAid(id):
    if ("av" in id) or ("AV" in id):
        return id[2:]
    elif ("BV" in id):
        site = "https://api.bilibili.com/x/web-interface/view?bvid=" + id
        lst = codecs.decode(requests.get(site).content, "utf-8").split("\"")
        return str(lst[16][1:-1])

with open("./fast_check/source/pick_data.csv","r",encoding="utf-8-sig",newline='') as csvfile:
    listed = csv.DictReader(csvfile)
    min_time = datetime.datetime.today() + datetime.timedelta(days=-10)
    with open("./fast_check/source/pick.csv","w",encoding="utf-8-sig",newline='') as csvwrite:
        writefile = csv.writer(csvwrite)
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
            if owner == "无需作答":
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
            getVideo(turnAid(typeText.get()))
            root.destroy()
        yesButton = tkinter.Button(text="确定",font=("HarmonyOS Sans SC",10),command = lambda: overCommand(top))
        yesButton.pack()
        top.mainloop()
        shutil.copy("./fast_check/ed.mp4","./custom/ed.mp4")
        shutil.copy("./fast_check/source/pick.csv","./custom/pick.csv")
        os.system("python second_main.py")