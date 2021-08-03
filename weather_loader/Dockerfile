FROM python:3.8

RUN mkdir /code
RUN mkdir /code/app
WORKDIR /code
COPY app/ app/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
