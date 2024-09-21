#!/bin/bash

cd ..


while true; do
  
  sleep 20

  git pull --rebase 
  killall python3
  
  sleep 400
done