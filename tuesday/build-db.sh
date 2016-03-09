#!/bin/sh

sudo rm -rf /var/lib/postgresql/tuesday-data
docker build -t stsilabs/past-tuesday-db ./db