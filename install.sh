#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $dir

virtualenv -p python2 ~/venvs/mint
source ~/venvs/mint/bin/activate
pip install -r requirements.txt

#Set environment variable in supervisord according to deploying environment (default to development)
case "$DEPLOY_ENVIRONMENT" in
    development)
		SETTINGS="config.DevelopmentConfig"
		;;
    test)
		SETTINGS="config.TestConfig"
		;;
    production)
		SETTINGS="config.ProductionConfig"
		;;
    *)
		SETTINGS="config.DevelopmentConfig"
		;;
esac

echo "Adding mint to supervisord..."
cat > /etc/supervisord.d/mint.ini << EOF
[program:mint]
command=$HOME/venvs/mint/bin/gunicorn --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app
directory=$dir
autostart=true
autorestart=true
user=$USER
environment=SETTINGS="$SETTINGS"
EOF
