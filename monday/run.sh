#!/bin/sh

docker build -t stsilabs/past-monday-www ./www

docker run -it -p "5000:5000" \
--env-file /home/vagrant/.env \
--name monday-www stsilabs/past-monday-www

docker stop monday-www && docker rm monday-www
