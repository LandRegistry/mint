#!/bin/bash

yum install -y python-devel
pip install virtualenv
pip install virtualenvwrapper

echo "Configure virtualenvwrapper..."
cat >> /home/vagrant/.bashrc << EOF
  export WORKON_HOME='/home/vagrant/venvs'
  source /usr/bin/virtualenvwrapper.sh
EOF
