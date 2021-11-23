FROM python:3.8.12-buster

COPY fobokiller /fobokiller

COPY requirements_docker.txt /requirements_docker.txt

RUN pip install --upgrade pip

RUN pip install -r requirements_docker.txt

RUN pip install gsutil


CMD python -m fobokiller.get_data
