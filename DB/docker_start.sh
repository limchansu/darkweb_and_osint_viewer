#!/bin/bash


cd mongodb
docker build -t setup-rspl .
cd ..
docker-compose up -d