# Thanks
# http://stackoverflow.com/questions/30624829/no-such-file-or-directory-limits-h-when-installing-pillow-on-alpine-linux

FROM python:2.7-alpine
ADD . /www

RUN apk add --update libpq python-dev postgresql-dev gcc musl-dev
WORKDIR /www
RUN pip install -r requirements.txt

CMD ["python", "-B", "__main__.py"]