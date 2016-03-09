#!/bin/sh

sudo rm -rf /var/lib/postgresql/data
docker build -t stsilabs/past-tuesday-db ./db