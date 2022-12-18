# 音之墨音MAD排行榜

本项目是目前正在 B 站上持续发布的音之墨音MAD排行榜的自动化合成脚本，主要使用 Python 语言编写。
# 必需文件
## 所需要的其它依赖项
* [TEditor](https://github.com/SkiTiSu/TEditor)
* [Lux](https://github.com/iawia002/lux)
* HarmonyOS Sans SC 字体

## 必须填充的文件

* `custom/ed.mp4`
* `custom/staff.png`

## 选择性填充文件

* `custom/pick.csv`（Pick Up 作品）
* `custom/blacklist.csv`（黑名单作品）
* `custom/adjust.csv`（对某 UID 的作品评分进行系数调整）
* `custom/ads/*` （视频前的广告）

# 数据获取/合成

## 非自定义自动化获取数据（含评分、视频合成）
首先爬取数据。
>```python advanced_main.py```
随后进行视频合成。
>```python main.py```

## 自定义作品获取数据（仅数据）
在`custom/custom.csv`文件按格式填写`aid（作品 av 号，不含 av 前缀）`、`owner（自定义视频作者，非搬运请留空）`。
>```python custom.py```
随后请提取`data/customed.csv`，使用 TEditor 导入`template/main.ted`模板自行合成图片。
