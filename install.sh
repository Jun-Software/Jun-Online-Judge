#! /bin/bash
apt-get install git
yum install git
dnf install git
emerge --ask --verbose dev-vcs/git
pacman -S git
zypper install git
urpmi git
nix-env -i git
pkg install git
pkgutil -i git
pkg install developer/versioning/git
pkg_add git
apk add git
tazpkg get-install git
git clone https://gh.imjcj.eu.org/https://github.com/Jun-Software/Jun-Online-Judge joj
cd joj
python3 get-pip.py
pip3 install -r requirements.txt
echo "默认管理员账号密码均为admin"
echo "[Unit]" > /usr/lib/systemd/system/joj.service
echo "Description=Jun Online Judge" >> /usr/lib/systemd/system/joj.service
echo "After=network.target" >> /usr/lib/systemd/system/joj.service
echo "[Service]" >> /usr/lib/systemd/system/joj.service
echo "ExecStart=/usr/bin/python3 $(pwd)/index.py" >> /usr/lib/systemd/system/joj.service
echo "[Install]" >> /usr/lib/systemd/system/joj.service
echo "WantedBy=multi-user.target" >> /usr/lib/systemd/system/joj.service
echo "使用'sudo systemctl start joj.service'启动JOJ"
echo "使用'sudo systemctl stop joj.service'停止JOJ"
echo "使用'sudo systemctl restart joj.service'重启JOJ"
echo "使用'sudo systemctl enable joj.service'设置开机启动JOJ"
echo "使用'sudo systemctl disable joj.service'取消开机启动JOJ"
echo "使用'sudo systemctl status joj.service'查看JOJ状态"