from datetime import timedelta
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
 
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'khong-doan-noi-dau'
    JWT_SECRET_KEY = 'super_secret'
    ACCESS_EXPIRES = timedelta(hours=1)
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:damthuhang2010@testrds.cxmkaq0ig18s.us-east-1.rds.amazonaws.com/thu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')