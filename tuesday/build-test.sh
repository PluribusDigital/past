#!/bin/sh

sudo rm -rf /var/lib/postgresql/tuesday-test-data
docker build -t tuesday-test-db \
-f /home/vagrant/tuesday/db/Dockerfile-testing \
/home/vagrant/tuesday/db

docker run -it -p "5432:5432" \
--env-file /home/vagrant/.env \
-e "POSTGRES_DB=tuesday" \
-v "/var/lib/postgresql/tuesday-test-data:/var/lib/postgresql/data" \
--name tuesday-db tuesday-test-db

docker stop tuesday-db && docker rm tuesday-db