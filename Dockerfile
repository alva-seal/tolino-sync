# set base image (host OS)
FROM python:3.9

LABEL org.opencontainers.image.description tolino-sync to tolino cloud and optional with calibre

RUN apt-get update
#RUN apt-get install -y ffmpeg

# set the working directory in the container
WORKDIR /config

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY code/ .

# command to run on container start
CMD [ "python", "./sealbot.py" 
