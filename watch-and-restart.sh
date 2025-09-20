#!/bin/bash

./stop.sh
while : ; do
  echo
  date
  ./weather.sh &> weather.log &
  sleep 5
  echo "============= LOG ============="
  cat weather.log
  echo "==============================="
  echo
  echo "Waiting for changes"
  inotifywait ./ -e CLOSE_WRITE --include open_weather\.py
  ./stop.sh
done
