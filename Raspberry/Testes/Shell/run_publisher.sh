#!/bin/bash

#add local ip address in raspberry

#change to the scripts directory
# cd /home/intermidia/enoe/publisher-raspberry

while true
do
    killall python3

    echo "Starting The Publishing"

    sleep 5

    # Run Python code in the background
    python3 ultrassonic_file_writer.py &
    python3 ultrassonic_file_reader.py &
    python3 check_connection.py &
   

    # Wait for all background processes to complete
    wait
done