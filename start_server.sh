#!/usr/bin/env bash

nohup python data-producer.py $1:9092 stock-analyzer 5000 > data-producer.log 2> data-producer.err < /dev/null &
nohup python data-storage.py stock-analyzer $1:9092 stock stock $1 > data-storage.log 2> data-storage.err < /dev/null &
nohup python redis-publisher.py average-stock-price $1:9092 average-stock-price $1 6379 > redis-publisher.log 2> redis-publisher.err < /dev/null &
log.io-server &
log.io-harvester &

cd nodejs
npm install

node index.js --port=3000 --redis_host=$1 --redis_port=6379 --subscribe_topic=average-stock-price &