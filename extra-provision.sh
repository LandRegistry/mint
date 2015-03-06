localectl set-locale LANG=en_GB.UTF-8
timedatectl set-timezone Europe/London
yum install -y supervisor
systemctl enable supervisord
systemctl start supervisord
chown root:vagrant /etc/supervisord.d
chmod g+w /etc/supervisord.d
sudo -i -u vagrant source /home/vagrant/srv/mint/install.sh
sudo supervisorctl reload

echo "Adding a nice bunch of aliases..."
cat >> /home/vagrant/.bashrc << EOF
  alias start="sudo supervisorctl start"
  alias stop="sudo supervisorctl stop"
  alias restart="sudo supervisorctl restart"
  alias status="sudo supervisorctl status"
  alias reload="sudo supervisorctl reload"
EOF
