#!/bin/sh

docker build -t stsilabs/past-tuesday-www /home/vagrant/tuesday/www && \
docker push stsilabs/past-tuesday-www && \
docker-cloud service redeploy www
