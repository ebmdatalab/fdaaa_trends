#!/bin/bash

docker build -t datalab-jupyter -f Dockerfile .
docker run --rm -ti --mount source=${PWD},dst=/home/app/notebook,type=bind -p 8888:8888 datalab-jupyter
