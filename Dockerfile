# pull official base image
FROM python:3.10-slim-bullseye

# This flag is important to output python logs correctly in docker
ENV PYTHONUNBUFFERED 1
# Flag to optimize container size a bit by removing runtime python cache
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir -p /lesa && apt update && apt upgrade -y && pip3 install --upgrade pip && apt install -y ffmpeg

WORKDIR /lesa

COPY requirements.txt .

RUN pip3 install -r requirements.txt

CMD rm requirements.txt
