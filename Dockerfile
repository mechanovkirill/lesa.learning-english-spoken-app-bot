# pull official base image
FROM python:3.10.5-slim-bullseye

# This flag is important to output python logs correctly in docker!
ENV PYTHONUNBUFFERED 1
# Flag to optimize container size a bit by removing runtime python cache
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update && pip3 install --upgrade pip && apt install -y ffmpeg

WORKDIR /lesa

#EXPOSE 5000

#VOLUME /app/data
#VOLUME /app/lesa_bot/logs

# copy project
COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "lesa_bot/__main__.py"]
