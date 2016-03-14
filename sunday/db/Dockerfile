FROM postgres
ADD https://s3.amazonaws.com/stsi-past/sunday-db-seed.tar.gz /var/tmp/
WORKDIR /docker-entrypoint-initdb.d
ADD schema.sql .
ADD seed.sql .
RUN ["tar", "-zxvf", "/var/tmp/sunday-db-seed.tar.gz"]
WORKDIR /
VOLUME /var/lib/postgresql/data
EXPOSE 5432