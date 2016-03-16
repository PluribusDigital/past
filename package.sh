#!/bin/sh

cd /home/vagrant/sunday/db
tar -zcvf /home/vagrant/deploy/sunday-db-seed.tar.gz ./seed

cd /home/vagrant/monday/www
tar -zcvf /home/vagrant/deploy/monday-www-source.tar.gz ./source/postagger

cd /home/vagrant/tuesday/db
tar -zcvf /home/vagrant/deploy/tuesday-db-seed.tar.gz ./seed
