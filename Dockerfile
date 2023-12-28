FROM ubuntu
RUN python3 get-pip.py
RUN pip3 install -r requirements.txt
