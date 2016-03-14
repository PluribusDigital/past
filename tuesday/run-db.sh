#!/bin/sh

docker run -it -p "2345:5432" \
-v "/var/lib/postgresql/tuesday-data:/var/lib/postgresql/data" \
--env-file /home/vagrant/.env \
-e "POSTGRES_DB=tuesday" \
--name tuesday-db stsilabs/past-tuesday-db

docker stop tuesday-db && docker rm tuesday-db
