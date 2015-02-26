import os

class Config(object):
    DEBUG = False
    SYSTEM_OF_RECORD = os.getenv('SYSTEM_OF_RECORD', 'http://127.0.0.1:5001')

class DevelopmentConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class PreviewConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class PreProductionConfig(Config):
    SYSTEM_OF_RECORD = 'http://192.168.39.5:5001'

class ProductionConfig(Config):
    SYSTEM_OF_RECORD = 'http://192.168.39.5:5001'
