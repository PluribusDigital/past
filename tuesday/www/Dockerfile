# Thanks
#

FROM python:3-alpine

RUN apk update
RUN apk add gcc musl-dev ca-certificates \
python-dev \
libpq postgresql-dev \
nodejs \
git

RUN npm install bower --global

ADD requirements.txt /
RUN pip install -r requirements.txt
RUN python -m nltk.downloader book
RUN python -m nltk.downloader snowball_data

# Add the javascript dependencies
ADD .bowerrc /
ADD bower.json /
RUN bower install

ADD . /www
WORKDIR /www
RUN python setup.py develop

EXPOSE 5000
CMD ["python", "-m", "api"]