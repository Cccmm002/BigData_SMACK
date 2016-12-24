#!/usr/bin/env bash

sudo apt-get update

sudo apt install -y python-pip

sudo apt install -y nodejs-legacy

sudo apt install -y npm

sudo npm update

sudo npm install -g log.io --user "ubuntu"

sudo /usr/bin/pip install --upgrade pip

sudo /usr/bin/pip install flask

sudo /usr/bin/pip install kafka-python

sudo /usr/bin/pip install googlefinance

sudo /usr/bin/pip install apscheduler

sudo /usr/bin/pip install cassandra-driver

rm ~/.log.io/harvester.conf
cp ~/harvester.conf ~/.log.io/