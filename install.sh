#! /bin/bash
bash <(curl https://gh.imjcj.eu.org/https://github.com/Jun-Software/Jun-Online-Judge/raw/master/nix.sh)
nix-env -i git
git clone https://gh.imjcj.eu.org/https://github.com/Jun-Software/Jun-Online-Judge
pip3 install -r requirements.txt
