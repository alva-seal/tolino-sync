# set base image (host OS)
FROM ghcr.io/linuxserver/baseimage-ubuntu:jammy

LABEL org.opencontainers.image.description tolino-sync to tolino cloud and optional with calibre
# set version label
ARG BUILD_DATE
ARG VERSION
LABEL build_version="${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="alva-seal"

RUN apt-get update 
#RUN apt-get install -y python pip calibre
RUN apt-get install -y vim

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY code/ .

VOLUME /config

# command to run on container start
CMD [ "python", "./tolino-sync.py"] 
