FROM python:3.8-buster

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY ./jukepybot /app/jukepybot

WORKDIR /app

CMD [ "flask", "run" ]
