#!/bin/sh

docker run -it -p "5432:5432" \
-v "/var/lib/postgresql/sunday-data:/var/lib/postgresql/data" \
--env-file /home/vagrant/.env \
-e "POSTGRES_DB=sunday" \
--name sunday-db stsilabs/past-sunday-db

docker stop sunday-db && docker rm sunday-db
