#!/bin/bash

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $dir

#Re-link venv to python in case anything's different
find ~/venvs/mint -type l -delete
virtualenv -p python2 ~/venvs/mint
source ~/venvs/mint/bin/activate

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
	release)
		SUPERVISOR_ENV="SETTINGS=\"config.ReleaseConfig\""
		COMMAND="$HOME/venvs/mint/bin/python run.py"
		;;
    preproduction)
		SUPERVISOR_ENV="SETTINGS=\"config.PreProductionConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 16 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
		;;
    oat)
		SUPERVISOR_ENV="SETTINGS=\"config.OatConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 16 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
		;;
    production)
		SUPERVISOR_ENV="SETTINGS=\"config.ProductionConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 16 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
		;;
    newa)
		SUPERVISOR_ENV="SETTINGS=\"config.NewAConfig\""
		COMMAND="$HOME/venvs/mint/bin/gunicorn -w 16 --log-file=- --log-level DEBUG -b 0.0.0.0:5000 --timeout 120 application.server:app"
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
