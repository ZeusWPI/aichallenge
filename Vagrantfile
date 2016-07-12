# -*- mode: ruby -*-
# vi: set ft=ruby :

# Config VB for version 2. See https://www.vagrantup.com/docs/vagrantfile/version.html.
Vagrant.configure(2) do |config|
  config.vm.define "dev", primary: true do |dev|
    dev.vm.box = "ubuntu/trusty64"
    dev.vm.network :forwarded_port, guest: 5000, guest_ip: '0.0.0.0', host: 5000, host_ip: '0.0.0.0'
    # Remote Python debugging
    dev.vm.network :forwarded_port, guest: 8080, guest_ip: '0.0.0.0', host: 15000, host_ip: '0.0.0.0'
    dev.vm.provision :shell, path: "battlebots/scripts/vagrant/vagrant_bootstrap.sh"
    dev.vm.hostname = "bottlebats-dev"
    dev.vm.synced_folder ".", "/vagrant"
    dev.vm.provider :virtualbox do |vb|
      vb.name = "bottlebats-vagrant-host"
      vb.memory = 1024
      # If 'vagrant up' is stuck, enable this line and check virtual box GUI.
      # this might help find out that e.g. virtualization was not enabled
      # on your machine.
      # vb.gui = true
    end

    # Makes host SSH keys available on the guest machine
    dev.ssh.forward_agent = true
  end
end
