#!/bin/bash

echo "Sleeping for 10 seconds to allow MongoDB to initialize..."
sleep 10  # MongoDB가 준비될 시간을 대기

echo "Running Replica Set initialization..."
mongosh mongodb://mongo1:27017 --file /usr/src/configs/replicaSet.js
