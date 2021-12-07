import socket
import sys
import json
import argparse
import select
import logging
from datetime import time

import logs.config_server_log
from decos import log

from common.utils import get_message, send_meccage
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER
from errors import IncorrectDataRecivedError

SERVER_LOGGER = logging.getLogger('server')

@log
def process_client_massage(message, messages_list, client):
    SERVER_LOGGER.debug(f'Разбор сетевого сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_meccage(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        SERVER_LOGGER.error(f'Пришло сообщение {message[MESSAGE_TEXT]}')
        return
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

@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


@log
def main():
    listen_address, listen_port = arg_parser()
    SERVER_LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(1)

    clients = []
    messages = []

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address} {clients}')
            clients.append(client)


        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_massage(get_message(client_with_message),
                                           messages, client_with_message)
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                       f'отключился от сервера.')
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: 1,
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            SERVER_LOGGER.info(f'Сообщение для клиента {message}.')
            for waiting_client in send_data_lst:
                try:
                    send_meccage(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)

        # except json.JSONDecodeError:
        #     SERVER_LOGGER.error(f'Не удалось декодировать JSON, полученный от клиента {client_address}.'
        #                         f'Соединение закрывается')
        #     client.close()
        # except IncorrectDataRecivedError:
        #     SERVER_LOGGER.error(
        #         f'От клиента {client_address} получены некорректные данные.'
        #         f'Соединение закрывается')
        #     client.close()

if __name__ == '__main__':
    main()