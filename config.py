import os

class Config(object):
    DEBUG = False
    SYSTEM_OF_RECORD = os.environ['SYSTEM_OF_RECORD']

class DevelopmentConfig(Config):
    SYSTEM_OF_RECORD = 'http://10.0.2.2:5001'
    DEBUG = True

class TestConfig(Config):
    SYSTEM_OF_RECORD = 'http://127.0.0.1:5001'
    DEBUG = True

class ProductionConfig(Config):
    SYSTEM_OF_RECORD = 'http://192.168.39.5:5001'
