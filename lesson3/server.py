import socket
import sys
import json

from lesson3.common.utils import get_message, send_meccage
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, RESPONDEFAULT_IP_ADRESS, \
    ERROR, DEFAULT_PORT, MAX_CONNECTIONS


def process_client_massage(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in \
            message and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    elif ACTION in message and message[ACTION] == PRESENCE and TIME in \
            message and USER in message and message[USER][ACCOUNT_NAME] != 'Guest':
        return {
        RESPONSE: 400,
        ERROR:'Unknown user'
        }
    return {
        RESPONSE: 400,
        ERROR:'Bad request'
    }

def main():
    try:
        if '-p' in sys.argv:
            lisen_port = int(sys.argv[sys.argv.index('-p')+1])
        else:
            lisen_port = DEFAULT_PORT
        if lisen_port <1024 or lisen_port >65535:
            raise ValueError
    except IndexError:
        print(' Необходимо ввести номер порта после параметра \'-p\'')
        sys.exit(1)
    except ValueError:
        print(' Номер порта не может быть меньше 1024 или больше 65565')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_adr = sys.argv[sys.argv.index('-a')+1]
        else:
            listen_adr = ''
    except IndexError:
        print(' Необходимо ввести ip адресс после параметра \'-a\'')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_adr,lisen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_massage(message_from_client)
            send_meccage(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорректное сообщение от клиента')
            client.close()

if __name__ == '__main__':
    main()