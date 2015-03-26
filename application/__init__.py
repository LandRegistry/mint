from flask import Flask, request
import os
from python_logging.setup_logging import setup_logging

setup_logging()
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
