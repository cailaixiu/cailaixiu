# 才来修

### 问题由来
在一些医院、学校、机关、企业单位中，仍旧采用电话报修的方式来解决信息系统中碰到的各种软硬件问题。传统的基于WEB的问题跟踪系统并不适合，主要原因是使用过于复杂、填报内容无法简化。最终，还是回到了电话报修的老路上来；占线、接报人员各种原因忙，问题的电子化记录基本上不可能实现；设立专门的呼叫中心，成本大大增加。

### 解决方案
在终端PC上，安装一个浮动窗口应用。用户遇到问题时，无需离开问题页面，一键完成报修。报修过程中通常需要的参数：IP、物理位置、分机、电脑参数、使用者、时间、截屏等等自动发送给IT人员。
![client](/images/client.png?raw=true)

### 功能列表
- 一键报修
- 接报提醒、反馈提醒
- 分级报修、手工与自动派单
- 报修仪表盘
- 标签化的知识库
- 终端登记管理
- 问题处理能力图表化
- 移动端状态跟踪
- 支持隔离网（内网）与非隔离网（外网）的企业局域网环境

### 客户端（Win7+）安装步骤
1. 下载help.exe 与 config.ini, 然后放在同一目录下
2. 修改config.ini中local_server，指向本地服务器
3. 点击help.exe执行，无需安装。在生产环境下，批量安装的客户端，推荐开机启动

### 服务器端(Windows)安装步骤
1. 下载并安装 [Mongodb](https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2012plus-4.2.6-signed.msi)
2. 下载clxserv.exe，直接运行
3. 启动后，推荐谷歌或火狐浏览器打开 http://localhost:8080  管理员用户名：admin 初始密码：admin


