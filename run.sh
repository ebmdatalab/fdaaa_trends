#!/bin/bash

docker build -t fdaaa_trends -f config/fdaaa_trends.Dockerfile .
docker run -ti -v ${PWD}:/usr/local/bin/fdaaa_trends -p 8888:8888 fdaaa_trends