#!/bin/bash

apt-get update
apt-get -y upgrade

apt-get install python-pytest
apt-get install python-flask

cd ~

wget https://dl.google.com/go/go1.12.7.linux-amd64.tar.gz
tar -xvf go1.12.7.linux-amd64.tar.gz
