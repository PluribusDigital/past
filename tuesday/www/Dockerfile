# Thanks

FROM python:3-alpine

RUN apk add --update libpq python-dev postgresql-dev gcc musl-dev

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /www
WORKDIR /www

CMD ["python", "-B", "-m", "api"]