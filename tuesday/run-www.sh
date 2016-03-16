#!/bin/sh

docker rmi $(docker images -f "dangling=true" -q)

docker build -t stsilabs/past-tuesday-www /home/vagrant/tuesday/www

docker run -d -p "5432:5432" \
--env-file /home/vagrant/.env \
-e "POSTGRES_DB=tuesday" \
-v "/var/lib/postgresql/tuesday-data:/var/lib/postgresql/data" \
--name tuesday-db stsilabs/past-tuesday-db

docker run -it -p "5000:5000" \
--link tuesday-db:db  \
--env-file /home/vagrant/.env \
-e "POSTGRES_DB=tuesday" \
-e "POSTGRES_HOST=db" \
-v "/home/vagrant/tuesday/www/app:/www/app" \
--name tuesday-www stsilabs/past-tuesday-www

docker stop tuesday-db && docker rm tuesday-db
docker stop tuesday-www && docker rm tuesday-www

#-v "/home/vagrant/tuesday/www/api:/www/api" \
