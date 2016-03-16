FROM postgres
ADD https://s3.amazonaws.com/stsi-past/tuesday-db-seed-2016-03-14.tar.gz \
    /var/tmp/source.tar.gz

WORKDIR /docker-entrypoint-initdb.d

ADD *.sql ./
RUN ["tar", "-zxvf", "/var/tmp/source.tar.gz"]
RUN ["rm", "-rf", "/var/tmp/"]

WORKDIR /

VOLUME /var/lib/postgresql/data
EXPOSE 5432
