#!/bin/sh

cd ./sunday/db
tar -zcvf ../../deploy/sunday-db-seed.tar.gz ./seed
cd ../../monday/www
tar -zcvf ../../deploy/monday-www-source.tar.gz ./source/postagger
cd ../../tuesday/db
tar -zcvf ../../deploy/tuesday-db-seed.tar.gz ./seed
