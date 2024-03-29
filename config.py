import os
from datetime import timedelta

class ConfigDebug():
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/Bank'
    SECRET_KEY = os.environ.get("SECRET_KEY", 'super secret key')
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", '1241848918926306')
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_FRESHNESS_GRACE_PERIOD = 1
    # SECURITY_TOKEN_MAX_AGE = 10



    #min setup på mailtrap
    MAIL_SERVER='sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '58d9c9a416909a'
    MAIL_PASSWORD = '67e4ae70d0ef4b'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False