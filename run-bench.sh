#!/bin/sh

set -v

python main.py -n 4lanes -d bench -t 3600
python main.py -n 4lanes -d 640 -t 3600
python main.py -n 4lanes -d 960 -t 3600
python main.py -n 4lanes -d 1280 -t 3600
python main.py -n 4lanes -d 2560 -t 3600
python main.py -n 4lanes -d 3840 -t 3600
python main.py -n 4lanes -d 5120 -t 3600
python main.py -n 4lanes -d 6400 -t 3600
