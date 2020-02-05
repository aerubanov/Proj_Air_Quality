FROM python:3.7

RUN mkdir /code
RUN mkdir /code/src
WORKDIR /code
COPY . ./src
RUN pwd
RUN ls


RUN pip install -r ./src/web/loader/requirements.txt