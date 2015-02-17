yum install -y python-devel

yum install -y python-pip

yum groupinstall -y "Development Tools"

pip install -r /vagrant/code/mint/requirements.txt
