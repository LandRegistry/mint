# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

$xtra_prov = <<SCRIPT
localectl set-locale LANG=en_GB.UTF-8
timedatectl set-timezone Europe/London
yum install -y supervisor
systemctl enable supervisord
systemctl start supervisord
chown root:vagrant /etc/supervisord.d
chmod g+w /etc/supervisord.d
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "landregistry/centos-beta"
  config.vm.synced_folder ".", "/home/vagrant/srv/mint", create: true    
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.provision :shell, :inline => $xtra_prov
  config.vm.provision :shell, :path => 'provision.sh'

end
