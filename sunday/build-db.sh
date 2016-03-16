#!/bin/sh

sudo rm -rf /var/lib/postgresql/sunday-data
docker build -t stsilabs/past-sunday-db /home/vagrant/sunday/db