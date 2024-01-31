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
python3 index.py