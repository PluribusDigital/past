#!/bin/sh

docker run -it -p "5432:5432" \
-v "/var/lib/postgresql/data:/var/lib/postgresql/data" \
--env-file /home/vagrant/.env \
--name db stsilabs/past-tuesday-db

docker stop db && docker rm db
