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
