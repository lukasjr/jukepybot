FROM python:3.7-slim-buster

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY ./jukepybot /app/jukepybot

COPY setup.sh /app

WORKDIR /app

CMD [ "./setup.sh" ]
