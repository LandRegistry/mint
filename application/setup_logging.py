import os
import logging.config

import yaml

def setup_logging():

    path = 'python-logging/logging.yaml'

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
