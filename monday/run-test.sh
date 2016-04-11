#!/bin/sh

docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
docker rmi $(docker images -f "dangling=true" -q)

docker build -t stsilabs/past-monday-www /home/vagrant/monday/www

docker run -it -p "5000:5000" \
--env-file /home/vagrant/.env \
--name monday-www stsilabs/past-monday-www python -B -m pytest --maxfail=10

docker stop monday-www && docker rm monday-www

# python -B -m pytest --maxfail=10