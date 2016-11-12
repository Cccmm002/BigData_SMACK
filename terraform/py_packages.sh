#!/usr/bin/env bash

sudo yum install nodejs npm --enablerepo=epel

sudo /usr/bin/pip install --upgrade pip

sudo /usr/local/bin/pip install flask

sudo /usr/local/bin/pip install kafka-python

sudo /usr/local/bin/pip install googlefinance

sudo /usr/local/bin/pip install apscheduler

sudo /usr/local/bin/pip install cassandra-driver

sudo npm install nogger -g