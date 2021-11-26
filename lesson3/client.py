import sys
import socket
import json

from common.utils import send_meccage, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, DEFAULT_IP_ADRESS, DEFAULT_PORT, \
    RESPONSE, ERROR
import time

def create_presence(account_name = 'Guest'):
    out_massage = {
        ACTION:PRESENCE,
        TIME:time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out_massage

def process_answer(message):
    if RESPONSE in message:
        if message[RESPONSE] == '200':
            return '200: все норм'
        print(message)
    return f'400:{message[ERROR]}'
    raise ValueError




def main():
    try:
        server_adr = sys.argv[1]
        server_port = sys.argv[2]
        if server_port <1024 or server_port> 65535:
            raise ValueError
    except IndexError:
        server_adr = DEFAULT_IP_ADRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print(' Номер порта не может быть меньше 1024 или больше 65565')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    transport.connect((server_adr,server_port))
    message_to_server = create_presence()
    send_meccage(transport, message_to_server)
    try:
        answer = process_answer(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение')

if __name__ == '__main__':
    main()