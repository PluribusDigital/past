FROM python:2.7-alpine
RUN apk add --update libpq python-dev
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "__main__.py"]