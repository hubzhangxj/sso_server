#!/bin/bash
#wget https://bootstrap.pypa.io/get-pip.py
#python get-pip.py

sudo apt-get install memcached
sudo apt-get install apache2
sudo apt-get install apache2-threaded-dev
sudo apt-get install libapache2-mod-wsgi

pip install django==1.11.8
pip install django-suit
pip install apscheduler
pip install python-memcached
pip install whitenoise
pip install mod_wsgi
