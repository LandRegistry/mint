import os

class Config(object):
    DEBUG = False
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')
    LOGGING_PATH = os.getenv('LOGGING_PATH', 'python_logging/logging.yaml')

class DevelopmentConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class PreviewConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class ReleaseConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class PreProductionConfig(Config):
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')

class OatConfig(Config):
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')

class ProductionConfig(Config):
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')

class NewAConfig(Config):
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')
