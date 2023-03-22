FROM python:3.11.2-alpine3.17
COPY requirements.txt /temp/requirements.txt
COPY service ./service
RUN apk add postgresql-client build-base postgresql-dev
RUN pip install --upgrade pip
EXPOSE 8000
RUN pip install -r /temp/requirements.txt
WORKDIR /service



