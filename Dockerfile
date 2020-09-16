FROM ubuntu:20.04

LABEL maintainer="xudian.cn@gmail.com"
ENV ddl_debug=False
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV ddl_env=production
RUN mkdir /config
COPY requirements.txt /config
COPY docker/supervisord-dev.conf /config
COPY docker/supervisord.conf /config
ADD . /app
WORKDIR /app
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y install curl zip unzip python3 python3-dev python3-pip supervisor python-is-python3
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --no-cache-dir -r /config/requirements.txt
RUN pip3 install daphne