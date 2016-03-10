# -*- mode: ruby -*-
# vi: set ft=ruby :

project = "past"
container_root = "/home/vagrant"

PORTS = %w(8080 8081 8082 2345 2346 5000)

# ----------------------------------------------------------------------------- 
# Configure the VM
# ----------------------------------------------------------------------------- 
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false

  PORTS.each do |p|
    config.vm.network "forwarded_port", guest: p, host: p
  end

  config.vm.synced_folder ".", "#{container_root}"

  config.vm.provider "virtualbox" do |v|
    v.name = project
	v.memory = 2000
	v.cpus = 2
  end

  # https://github.com/Varying-Vagrant-Vagrants/VVV/issues/517
  config.vm.provision "fix-no-tty", type: "shell" do |s|
    s.privileged = false
    s.inline = "sudo sed -i '/tty/!s/mesg n/tty -s \\&\\& mesg n/' /root/.profile"
  end

  # Install docker
  config.vm.provision "docker"

  # Install docker-compose
  config.vm.provision "docker-compose", type: "shell", inline: <<-EOC
    curl -L https://github.com/docker/compose/releases/download/1.6.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
  	chmod +x /usr/local/bin/docker-compose
  EOC
end
