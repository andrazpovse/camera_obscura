#!/bin/sh

export PYTHONPATH=$PYTHONPATH:/home/pi/.local/lib/python3.7/site-packages

# Script that will be starting after bootup (cronjob).
# Starts the python code.
cd /
cd home/pi/camera_obscura
sudo python3 main.py
cd /
