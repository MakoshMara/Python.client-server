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
    ERROR, DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from errors import IncorrectDataRecivedError

SERVER_LOGGER = logging.getLogger('server')

@log
def process_client_massage(message, messages_list, client, clients, names):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_meccage(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_meccage(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return

    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_meccage(client, response)
        return
@log
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_meccage(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')

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

    names = dict()

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)


        recv_data_lst = []
        send_data_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_massage(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: 1,
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            SERVER_LOGGER.info(f'Сообщение для клиента {message[DESTINATION]}: {message}.')

if __name__ == '__main__':
    main()