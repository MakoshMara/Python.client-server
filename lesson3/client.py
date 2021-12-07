import argparse
import logging
import sys
import socket
import json
import logs.config_client_log

from common.utils import send_meccage, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, DEFAULT_IP_ADRESS, DEFAULT_PORT, \
    RESPONSE, ERROR, MESSAGE
import time

from common.variables import SENDER, MESSAGE_TEXT
from decos import log
from errors import ReqFieldMissingError

CLIENT_LOGGER = logging.getLogger('client')

@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')

@log
def create_message(sock, account_name = 'Guest'):
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    out_massage = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформированно сообщение серверу: {out_massage}')
    return out_massage

@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

@log
def process_answer(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOGGER.debug(f'Сообщение успешно обработано сервером')
            return '200: все норм'
        CLIENT_LOGGER.error(f'При обработке сервером обнаружена ошибка:{message[ERROR]}')
        return f'400:{message[ERROR]}'
    raise ValueError

@log
def arg_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')


    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')


    return server_address, server_port, client_mode

@log
def main():
    server_adr, server_port, client_mode = arg_parser()
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_adr}, '
        f'порт: {server_port}, режим работы: {client_mode}')

    try:
        transport = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        transport.connect((server_adr,server_port))
        send_meccage(transport, create_presence())
        CLIENT_LOGGER.info(f'Серверу отправлено сообщение')
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера:{answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Не удалось декодировать JSON от сервера')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_adr}:{server_port} '
                               f'Сервер отверг запрос на подключение')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутвует необходимое поле '
                            f'{missing_error.missing_field}')
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            if client_mode == 'send':
                try:
                    send_meccage(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_adr} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        CLIENT_LOGGER.error(f'Соединение с сервером {server_adr} было потеряно.')
                        sys.exit(1)

if __name__ == '__main__':
    main()