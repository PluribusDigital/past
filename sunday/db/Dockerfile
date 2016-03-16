FROM postgres
ADD https://s3.amazonaws.com/stsi-past/sunday-db-seed.tar.gz /var/tmp/source.tar.gz
WORKDIR /docker-entrypoint-initdb.d

ADD *.sql ./
RUN ["tar", "-zxvf", "/var/tmp/source.tar.gz"]
RUN ["rm", "-rf", "/var/tmp/"]

WORKDIR /
VOLUME /var/lib/postgresql/data
EXPOSE 5432