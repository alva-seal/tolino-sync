# set base image (host OS)
FROM ghcr.io/linuxserver/baseimage-ubuntu:noble

LABEL org.opencontainers.image.description="tolino-sync to tolino cloud and optional with calibre"
# set version label
ARG BUILD_DATE
ARG VERSION
LABEL build_version="${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="alva-seal"

RUN apt-get update 
#RUN apt-get install -y python pip calibre
RUN apt-get install -y vim
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN apt-get install -y git

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install --break-system-packages -r requirements.txt
RUN pip install --break-system-packages git+https://github.com/alva-seal/pytolino.git 

# copy the content of the local src directory to the working directory
COPY code/ .

VOLUME /config

# command to run on container start
CMD [ "python3", "main.py"]
#CMD ["gunicorn","main:app", "-c", "gunicorn_config.py"]

VOLUME /config
VOLUME /library
