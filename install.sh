#! /bin/bash
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi
bash <(curl https://hydro.ac/nix.sh)
nix-env -i git
git clone https://gh.imjcj.eu.org/https://github.com/Jun-Software/Jun-Online-Judge
pip3 install -r requirements.txt