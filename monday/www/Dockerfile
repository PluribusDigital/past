# Thanks
# http://stackoverflow.com/questions/30624829/no-such-file-or-directory-limits-h-when-installing-pillow-on-alpine-linux

FROM anapsix/alpine-java

RUN apk update
RUN apk add gcc musl-dev ca-certificates \
            python py-pip python-dev build-base \
            libpq postgresql-dev

RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update py-numpy@testing

ADD requirements.txt /
RUN pip install -r requirements.txt
RUN python -m nltk.downloader book
RUN python -m nltk.downloader snowball_data

#ADD https://s3.amazonaws.com/stsi-past/monday-www-source.tar.gz /var/tmp/
#RUN ["tar", "-zxvf", "/var/tmp/monday-www-source.tar.gz"]
ADD ./source/postagger /source/postagger
ENV CLASSPATH "/source/postagger"
ENV STANFORD_MODELS "/source/postagger/models"

WORKDIR /usr/src

ADD ./nlp ./nlp
ADD setup.py ./

RUN python setup.py develop

EXPOSE 5000
CMD ["python", "-m", "nlp"]