#!/usr/bin/env bash

locale-gen en_IE.UTF-8
locale-gen nl_BE.UTF-8
useradd -s /bin/bash -m -d /home/bottlebats bottlebats
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Belnet repositories for ludicrous speed!
cat > /etc/apt/sources.list << EOF
deb http://ftp.belnet.be/ubuntu.com/ubuntu trusty main restricted universe multiverse
deb http://ftp.belnet.be/ubuntu.com/ubuntu trusty-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu trusty-security main restricted universe multiverse
EOF

# Create database and database user
sudo -u postgres psql << EOF
create user bottlebats with password 'zeusisdemax';
create database bottlebats owner bottlebats;
EOF


cd /vagrant

easy_install pip
pip install -r ../requirements.txt
cp config.sample.py config.py
