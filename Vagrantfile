# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.define "dev", primary: true do |dev|
    dev.vm.box = "ubuntu/trusty64"
    dev.vm.network :forwarded_port, guest: 5000, guest_ip: '0.0.0.0', host: 5000, host_ip: '0.0.0.0'
    # remote Python debugging
    dev.vm.network :forwarded_port, guest: 8080, guest_ip: '0.0.0.0', host: 15000, host_ip: '0.0.0.0'
    dev.vm.provision :shell, path: "scripts/vagrant/vagrant_bootstrap.sh"
    dev.vm.hostname = "bottlebats-dev"
    dev.vm.synced_folder "."
    dev.vm.provider :virtualbox do |vb|
      vb.name = "bottlebats-vagrant-host"
      vb.memory = 1024
      # If 'vagrant up' is stuck, enable this line and check virtual box GUI.
      # this might help find out that e.g. virtualization was not enabled
      # on your machine.
      # vb.gui = true
    end

    # makes host SSH keys available on the guest machine
    dev.ssh.forward_agent = true
  end

  # A "rehearsal" machine that will mimic a staging/production setup. You'll
  # probably use this in conjunction with `fab rehearse install` and
  # `fab rehearse deploy` (it's basically an empty Ubuntu box).
  #
  # The server will be accessible on port 5080 (HTTP) and 5443 (HTTPS).
  #
  # Not used by default; run `vagrant up rehearsal`
  config.vm.define "rehearsal", autostart: false do |r|
    r.vm.box = "ubuntu/trusty64"
    r.vm.network :forwarded_port, guest: 22, host: 2223, id: 'ssh'
    r.vm.network :forwarded_port, guest: 80, guest_ip: '0.0.0.0', host:5080, host_ip: '0.0.0.0'
    r.vm.network :forwarded_port, guest: 443, guest_ip: '0.0.0.0', host:5443, host_ip: '0.0.0.0'
    r.vm.hostname = "rehearsal"
    r.vm.provider :virtualbox do |vb|
      vb.name = "bottlebats-rehearsal-host"
      # if 'vagrant up' is stuck, enable this line and check virtual box GUI.
      # this might help find out that e.g. virtualization was not enabled
      # on your machine.
      # vb.gui = true
    end
  end
end
