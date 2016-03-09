#!/bin/sh

docker build -t stsilabs/past-sunday-www ./www

docker run -d -p "5432:5432" \
-v "/var/lib/postgresql/sunday-data:/var/lib/postgresql/data" \
-e "POSTGRES_DB=sunday" \
--name sunday-db stsilabs/past-sunday-db

docker run -it -p "5000:5000" \
--link sunday-db:db  \
--env-file /home/vagrant/.env \
--name sunday-www stsilabs/past-sunday-www

docker stop sunday-db && docker rm sunday-db
docker stop sunday-www && docker rm sunday-www