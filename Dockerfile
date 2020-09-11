FROM ubuntu:20.04

LABEL maintainer="xudian.cn@gmail.com"

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV ddl_env production
RUN mkdir /config
COPY requirements.txt /config
ADD . /app
WORKDIR /app
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y install python3 python3-dev python3-pip gcc g++ libseccomp-dev cmake git software-properties-common python-is-python3 \
	openjdk-14-jdk golang-go && cd /tmp && git clone --depth=1 https://github.com/4ddl/ddlc && cd ddlc \
	&& mkdir build && cd build && cmake .. && make && make install && cd /tmp && git clone https://github.com/4ddl/ddlcw \
	&& cd ddlcw && pip3 install -r requirements.txt && python3 setup.py install && apt-get clean && rm -rf /var/lib/apt/lists/* \
	&& mkdir /runner && useradd -u 12001 code
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --no-cache-dir -r /config/requirements.txt
