#!/usr/bin/env bash
sudo apt-get install -y python-pandas
sudo pip uninstall -y kmx_cli
sudo pip install -I libs/astanin-python-tabulate-a6c585bd603c.zip
sudo python setup.py install

