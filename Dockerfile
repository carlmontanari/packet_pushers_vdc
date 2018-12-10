FROM ubuntu:18.04
RUN apt-get update && apt-get install -y \
    libffi-dev \
    ca-certificates \
    gcc make \
    musl-dev \
    git \
    sshpass \
    libxml2-dev \
    libxslt-dev \
    python3 \
    python3-dev \
    python3-pip \
    rsync
RUN python3 -m pip install ansible==2.7.4
RUN python3 -m pip install napalm==2.3.3
RUN python3 -m pip install napalm-ansible==0.10.0
