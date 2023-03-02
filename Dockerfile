
FROM python:3.11.1-slim-bullseye as Base

# This flag is important to output python logs correctly in docker
ENV PYTHONUNBUFFERED 1
# Flag to optimize container size a bit by removing runtime python cache
ENV PYTHONDONTWRITEBYTECODE 1

RUN useradd -rm -d /home/lesa -s /bin/bash -g root -G sudo -u 1001 -p "$(openssl passwd -1 lesa)" lesa

WORKDIR /home/lesa

RUN apt update  -y \
    && apt upgrade -y  \
    && pip3 install --upgrade pip  \
    && apt install -y python3-venv\
    && apt install -y build-essential libssl-dev libffi-dev python3-dev \
    && apt install -y ffmpeg \
    && python3 -m venv venv
#    && apt install -y libsndfile1\

COPY . .

RUN /home/lesa/venv/bin/pip install -r requirements.txt

CMD ["/home/lesa/venv/bin/python", "-m", "main"]

