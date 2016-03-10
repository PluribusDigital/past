# Thanks
#

FROM python:3-alpine

RUN apk update
RUN apk add gcc musl-dev ca-certificates
RUN apk add python-dev
RUN apk add libpq postgresql-dev

ADD requirements.txt /
RUN pip install -r requirements.txt
RUN python -m nltk.downloader book
RUN python -m nltk.downloader snowball_data

ADD . /www
WORKDIR /www
RUN python setup.py develop

CMD ["python", "-m", "api"]