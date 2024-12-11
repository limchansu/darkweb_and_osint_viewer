#!/bin/bash

sleep 10 | echo Sleeping

mongo mongodb://mongo1:27017 replicaSet.js
