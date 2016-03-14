#!/bin/sh

sudo rm -rf /var/lib/postgresql/tuesday-test-data
docker build -t tuesday-test-db -f ./db/Dockerfile-testing ./db

docker run -it -p "5432:5432" \
--env-file ~/.env \
-e "POSTGRES_DB=tuesday" \
-v "/var/lib/postgresql/tuesday-test-data:/var/lib/postgresql/data" \
--name tuesday-db tuesday-test-db

docker stop tuesday-db && docker rm tuesday-db
