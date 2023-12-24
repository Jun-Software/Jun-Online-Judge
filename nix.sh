#!/usr/bin/env bash
profile=~/.nix-profile/etc/profile.d/nix.sh

install_source=https://nixos.org/nix/install
mirror_ustc=https://mirrors.ustc.edu.cn
mirror_bfsu=https://mirrors.bfsu.edu.cn
channel=nixpkgs-unstable

curl -Is --connect-timeout 5 $mirror_ustc
ustc_reachable=$?
curl -Is --connect-timeout 5 $mirror_bfsu
bfsu_reachable=$?

if [ -f $profile ] && ! [ -x "$(command -v nix)" ]; then
    . $profile || true
fi

set -e
PATH=$PATH:/usr/sbin

if ! [ -x "$(command -v nix)" ]; then
    echo No nix found. Installing...
    if [ -x "$(command -v apk)" ]; then
        apk add xz curl bash shadow
    fi
    mkdir -p -m 0755 /nix
    if ! [ -x "$(command -v groupadd)" ]; then
        echo "groupadd command was required to run this script"
        exit
    fi
    groupadd nixbld -g 30000 || true
    for i in {1..10}; do
        useradd -c "Nix build user $i" -d /var/empty -g nixbld -G nixbld -M -N -r -s "$(which nologin)" "nixbld$i" || true
    done
    if ! [ -x "$(command -v xz)" ]; then
        if [ -f "/usr/bin/apt-get" ] && [ -f "/usr/bin/dpkg" ]; then
            apt-get update
            apt-get install xz-utils -y
        else
            echo "xz command was required to run this script"
            exit
        fi
    fi
    if [ -f "/snap/bin/curl" ]; then # Not compatible with snap curl
        snap remove curl || true
        if [ -f "/usr/bin/apt-get" ] && [ -f "/usr/bin/dpkg" ]; then
            apt-get update
            apt-get install curl -y
        elif ! [ -x "$(command -v wget)" ]; then
            echo "please install wget or curl, without snap."
            exit
        fi
    fi
    if [[ "$bfsu_reachable" == "0" ]]; then
        install_source=$mirror_bfsu/nix/latest/install
    elif [[ "$ustc_reachable" == "0" ]]; then
        install_source=$mirror_ustc/nix/latest/install
    fi
    sh <(curl -L $install_source) --no-daemon --no-channel-add
    echo ". $profile" >>~/.bashrc
    if [[ -f ~/.zshrc ]]; then
        echo ". $profile" >>~/.zshrc
    fi
    . $profile
    mkdir -p /etc/nix
fi

echo "substituters = $mirror_bfsu/nix-channels/store $mirror_ustc/nix-channels/store https://nix-bin.hydro.ac/" >/etc/nix/nix.conf    
echo "trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= hydro.ac:EytfvyReWHFwhY9MCGimCIn46KQNfmv9y8E2NqlNfxQ=" >>/etc/nix/nix.conf
echo "connect-timeout = 10" >>/etc/nix/nix.conf
echo "experimental-features = nix-command flakes" >>/etc/nix/nix.conf
if ! [ "$(nix-channel --list | grep nixpkgs)" ]; then
    if [[ "$bfsu_reachable" == "0" ]]; then
        nix-channel --add $mirror_bfsu/nix-channels/$channel nixpkgs
    elif [[ "$ustc_reachable" == "0" ]]; then
       nix-channel --add $mirror_ustc/nix-channels/$channel nixpkgs
    else
        nix-channel --add https://nixos.org/channels/$channel nixpkgs
    fi
fi
nix-channel --add https://nix-channel.hydro.ac/ hydro
echo "Now unpacking channel. might take a long time."
nix-channel --update
mkdir -p ~/.config/nixpkgs

set +e
