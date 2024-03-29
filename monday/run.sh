#!/bin/sh

docker rmi $(docker images -f "dangling=true" -q)

docker build -t stsilabs/past-monday-www /home/vagrant/monday/www

docker run -it -p "5000:5000" \
--env-file /home/vagrant/.env \
--name monday-www stsilabs/past-monday-www

docker stop monday-www && docker rm monday-www
