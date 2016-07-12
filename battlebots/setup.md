# How to set up an environment?
All instructions below are aimed at helping you set up a working development environment.
This would be enough to locally test your bot in the same conditions as on our production servers.
It would also allow you to help develop this wonderfull platform, if your cool like that.

## Requirements

Install [Vagrant](https://www.vagrantup.com/).

## Starting up

To create a Virtual Box completely in accordance to our system setup.
Simply go to the project root (where the Vagrant file is), and type `vagrant up`.
You can now ssh to the VB with `vagrant ssh`, and with a `cd /vagrant` you are now in the synced project root.
A complete virtual box is now at your disposal to test and develop your bots!


Use `vagrant reload` to reload the VB (when changes to the Vagrant-file are made;
and `vagrant provision` to execute the [provision script](battlebots/scripts/vagrant/vagrant_bootstrap.sh) again.
The webserver should restart automatically on detected changes, but you can start manually as well by executing dev_server.py.
To start the ranker (for automatically playing matches), start ranker.py.

## Logging

TODO

## Debugging

TODO

## Database acces

TODO

## FAQ

TODO

