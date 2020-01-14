SET mypath=%~dp0

docker build -t datalab-jupyter -f Dockerfile .
docker run --rm -ti --mount source=%mypath:~0,-1%,dst=/home/app/notebook,type=bind -p 8888:8888 datalab-jupyter
