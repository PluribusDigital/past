# Thanks
# http://stackoverflow.com/questions/30624829/no-such-file-or-directory-limits-h-when-installing-pillow-on-alpine-linux

#FROM python:3-alpine
FROM alpine

RUN apk update
RUN apk add gcc musl-dev ca-certificates
RUN apk add python py-pip python-dev build-base
RUN apk add libpq postgresql-dev

RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update py-numpy@testing

ADD requirements.txt /
RUN pip install -r requirements.txt
RUN python -m nltk.downloader book
RUN python -m nltk.downloader snowball_data

ADD . /www
WORKDIR /www

CMD ["python", "__main__.py"]