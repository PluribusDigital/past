#!/bin/sh

psql postgresql:///postgres --username "$POSTGRES_USER" -c 'CREATE DATABASE pasp_test;'
psql postgresql:///pasp_test --username "$POSTGRES_USER" -f /docker-entrypoint-initdb.d/schema.sql