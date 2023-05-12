FROM ubuntu
RUN apt update && apt upgrade -y && apt install -y python3 python3-pip
COPY dist/sf2-2.0.0-py3-none-any.whl /root/sf2-2.0.0-py3-none-any.whl
RUN pip3 install /root/sf2-2.0.0-py3-none-any.whl
RUN sf2 new -w -m foobar test.x