# 如果获取评论时最多只能获取到某个值（比如 20）条评论，
# 就说明需要登录：在下面填写 cookie
# 在浏览器中登录 bilibili，然后按 F12 打开开发者工具
# 方法一 切换到 Network 标签页，刷新页面，点击第一个请求，查看 Request Headers 中的 cookie 字段   
# 方法二 切换到 Application 标签页，在左侧点击 Cookies，选中 bilibili 域下域名，查看右侧的 cookie 字段
# 务必不要泄露、公开
# 详见 https://nemo2011.github.io/bilibili-api/#/get-credential

sessdata   = ""
bili_jct   = ""
buvid3     = ""
dedeuserid = ""
