import socket
import sys
import json
import logging
import logs.config_server_log

from lesson3.common.utils import get_message, send_meccage
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, DEFAULT_PORT, MAX_CONNECTIONS
from lesson3.errors import IncorrectDataRecivedError

SERVER_LOGGER = logging.getLogger('server')

def process_client_massage(message):
    SERVER_LOGGER.debug(f'Разбор сетевого сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in \
            message and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        SERVER_LOGGER.debug(f'Получено годное сообщение')
        return {RESPONSE: 200}
    elif ACTION in message and message[ACTION] == PRESENCE and TIME in \
            message and USER in message and message[USER][ACCOUNT_NAME] != 'Guest':
        SERVER_LOGGER.error(f'Пришло сообщение от неизвестного пользователя')
        return {
        RESPONSE: 400,
        ERROR:'Unknown user'
        }
    SERVER_LOGGER.error(f'Пришло пришло негодное сообщение')
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
        SERVER_LOGGER.critical(f'Не указан номер порта после параметра \'-p\'')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с недопустимым портом {lisen_port}. Номер порта  должен находиться в диапазоне от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_adr = sys.argv[sys.argv.index('-a')+1]
        else:
            listen_adr = ''
    except IndexError:
        SERVER_LOGGER.critical(f'Не указан адрес отправителя после параметра \'-a\'')
        sys.exit(1)

    SERVER_LOGGER.info(f'Сервер запущен. Порт для подключения: {lisen_port}. '
                       f'Адрес, с которого принимаются подключения: {listen_adr}. '
                       f'Если адрес не указан, принимаются сообщения с любого адреса')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_adr,lisen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение от пользователя:{message_from_client}')
            SERVER_LOGGER.debug(f'Сообщение от пользователя отправлено на обработку')
            response = process_client_massage(message_from_client)
            send_meccage(client, response)
            SERVER_LOGGER.info(f'Клиенту отправлен ответ: {response}, соединение закрывается')
            client.close()
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Не удалось декодировать JSON, полученный от клиента {client_address}.'
                                f'Соединение закрывается')
            client.close()
        except IncorrectDataRecivedError:
            SERVER_LOGGER.error(
                f'От клиента {client_address} получены некорректные данные.'
                f'Соединение закрывается')
            client.close()

if __name__ == '__main__':
    main()