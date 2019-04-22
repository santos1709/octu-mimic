#!/usr/bin/env bash

echo "  watcher-service:" > ././../docker-compose.yml
echo "    build: ./watcher" >> ././../docker-compose.yml
echo "    volumes:" >> ././../docker-compose.yml
echo "      - ./watcher:/usr/src/app" >> ././../docker-compose.yml
echo "    ports:" >> ././../docker-compose.yml
echo "      - 5100:8080" >> ././../docker-compose.yml
echo "    environment:" >> ././../docker-compose.yml
echo "      - CALLCOUNT" >> ././../docker-compose.yml
echo "" >> ././../docker-compose.yml

for i in {1..$1}
do
    echo "  api-service-$i:" >> ././../docker-compose.yml
    echo "    build: ./web-api" >> ././../docker-compose.yml
    echo "    volumes:" >> ././../docker-compose.yml
    echo "      - ./web-api:/usr/src/app" >> ././../docker-compose.yml
    echo "    ports:" >> ././../docker-compose.yml
    echo "      - 500$i:8080" >> ././../docker-compose.yml
    echo "    environment:" >> ././../docker-compose.yml
    echo "      - CALLCOUNT" >> ././../docker-compose.yml
    echo "      - MODELNAME" >> ././../docker-compose.yml
    echo "      - MODELVERSION" >> ././../docker-compose.yml
    echo "" >> ././../docker-compose.yml
    echo "" >> ././../docker-compose.yml
done

docker-compose up
