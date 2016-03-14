#!/bin/sh

docker rmi $(docker images -f "dangling=true" -q)

docker build -t stsilabs/past-tuesday-www ./www

docker run -d -p "5432:5432" \
--env-file ~/.env \
-e "POSTGRES_DB=tuesday" \
-v "/var/lib/postgresql/tuesday-test-data:/var/lib/postgresql/data" \
--name tuesday-db tuesday-test-db

docker run -it -p "5000:5000" \
--link tuesday-db:db  \
--env-file ~/.env \
-e "POSTGRES_DB=tuesday" \
-e "POSTGRES_HOST=db" \
--name tuesday-www stsilabs/past-tuesday-www python -B -m pytest -x

docker stop tuesday-db && docker rm tuesday-db
docker stop tuesday-www && docker rm tuesday-www
