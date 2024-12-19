#!/bin/bash

sleep 25

mongosh --host mongo1 --port 30001 --eval '
  rs.initiate({
    _id: "my-rs",
    members: [
      { _id: 0, host: "mongo1:30001" },
      { _id: 1, host: "mongo2:30002" },
      { _id: 2, host: "mongo3:30003" }
    ]
  });
'
