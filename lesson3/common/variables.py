import logging

DEFAULT_PORT = 7777
DEFAULT_IP_ADRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACAGE_LEGTH = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADRESS = 'responedefault_ip_adress'

LOGGING_LEVEL = logging.DEBUG
FORMATTER_DEFAULT = logging.Formatter('%(asctime)s %(levelname) -8s %(filename) -11s %(message)s')