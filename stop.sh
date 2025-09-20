#!/bin/bash

PID=$(ps afuxww | grep 'python open_weather.py' | grep -v grep | awk '{print $2}')

if [[ "$PID" != "" ]] ; then
  kill -9 $PID
fi
