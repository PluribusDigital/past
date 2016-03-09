# Thanks
# http://stackoverflow.com/questions/30624829/no-such-file-or-directory-limits-h-when-installing-pillow-on-alpine-linux

FROM python:2.7-alpine

RUN apk add --update libpq python-dev postgresql-dev gcc musl-dev

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /www
WORKDIR /www

CMD ["python", "-B", "__main__.py"]