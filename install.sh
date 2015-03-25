#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $dir

virtualenv -p python2 ~/venvs/mint
source ~/venvs/mint/bin/activate
pip install -r requirements.txt

#Create the logging directory as it is required by default
if [ ! -d $dir/logs ]; then
	mkdir $dir/logs
fi

#Set environment variable in supervisord according to deploying environment (default to development)
case "$DEPLOY_ENVIRONMENT" in
    development)
		SUPERVISOR_ENV="SETTINGS=\"config.DevelopmentConfig\""
		COMMAND="$HOME/venvs/mint/bin/python run.py"
		;;
    preview)
		SUPERVISOR_ENV="SETTINGS=\"config.PreviewConfig\""
		COMMAND="$HOME/venvs/mint/bin/python run.py"
		;;
    preproduction)
		SUPERVISOR_ENV="SETTINGS=\"config.PreProductionConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 8 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
		;;
    production)
		SUPERVISOR_ENV="SETTINGS=\"config.ProductionConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 8 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
		;;
    *)
		SUPERVISOR_ENV="SETTINGS=\"config.DevelopmentConfig\""
		COMMAND="$HOME/venvs/mint/bin/python run.py"
		;;
esac

if [ -n "$SYSTEM_OF_RECORD" ]; then
	SUPERVISOR_ENV="$SUPERVISOR_ENV,SYSTEM_OF_RECORD=\"$SYSTEM_OF_RECORD\""
fi

echo "Adding mint to supervisord..."
cat > /etc/supervisord.d/mint.ini << EOF
[program:mint]
command=$COMMAND
directory=$dir
autostart=true
autorestart=true
user=$USER
environment=$SUPERVISOR_ENV
stopasgroup=true
EOF
