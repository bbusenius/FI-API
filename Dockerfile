FROM ubuntu:19.10
LABEL maintainer="Brad Busenius https://github.com/bbusenius"
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx git
RUN pip3 install uwsgi
COPY ./ ./FI-API
WORKDIR ./FI-API
RUN pip3 install -r requirements.txt
COPY ./nginx.conf /etc/nginx/sites-enabled/default
CMD service nginx start && uwsgi -s /tmp/uwsgi.sock --chmod-socket=666 --manage-script-name --mount /=app:app
