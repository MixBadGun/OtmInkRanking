import time
import os
if os.path.exists("./custom/time.txt"):
    usedTime = str(open("./custom/time.txt","r").read())
else:
    usedTime = time.strftime("%Y%m%d", time.localtime())
    with open("./custom/time.txt","w") as f:
        f.write(usedTime)
main_max_title = 30
side_max_title = 23
pick_max_reason = 28
sep_time = 20 # 间隔时间
main_end = 15 # 主榜个数
side_end = 40 # 副榜个数
side_count = 4 # 副榜显示
staticFormat = ["png","jpg","jpeg"]