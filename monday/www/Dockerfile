# Thanks
# http://stackoverflow.com/questions/30624829/no-such-file-or-directory-limits-h-when-installing-pillow-on-alpine-linux

FROM python:3-alpine
RUN apk add --update libpq python-dev postgresql-dev gcc musl-dev ca-certificates

ADD . /www
WORKDIR /www
RUN pip install -r requirements.txt
RUN python -m nltk.downloader all

CMD ["python", "__main__.py"]