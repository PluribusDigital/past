#!/bin/sh

docker build -t stsilabs/past-monday-www ./www
docker run -it -p "5000:5000" stsilabs/past-monday-www