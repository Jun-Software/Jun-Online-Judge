# Jun-Online-Judge

一个简易、安全、高效的信息学在线评测系统。


<details>
<summary>部署教程</summary>

一键下载依赖（Linux）： `curl https://gh.imjcj.eu.org/https://raw.githubusercontent.com/Jun-Software/Jun-Online-Judge/master/install.sh | sudo bash`

手动下载依赖：
1. 安装`git`
2. 克隆此仓库，
> `git clone https://gh.imjcj.eu.org/https://github.com/Jun-Software/Jun-Online-Judge`
3. 安装`python3`
4. 用`pip`下载`requirements.txt`里的库
> `pip install -r requirements.txt`

手动部署：
1. 更改`config.py`内配置
2. 用`python3`运行`index.py`即可
> `python3 index.py`

温馨提示：

> 部署成功后，请勿再次配置`config.py`
</details>


<details>
<summary>使用教程</summary>

服务器部署成功后，

点击右上角`Login`登陆，

管理员账号为：`admin`，

管理员密码已在`config.py`配置。

登陆完成后，点击右上角`Welcome, admin`，

选择`Control Panel`

再登录一次管理员账号，

即可进入`Control Panel`，

可配置题目、备份数据、创建比赛。

附加说明：

题目评测数据压缩包（文件树）：
.
├─1.in
├─1.out
├─2.in
├─2.out
…

</details>
