import argparse
import logging
import sys
import socket
import json
import logs.config_client_log
import time
import threading

from common.utils import send_meccage, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, DEFAULT_IP_ADRESS, DEFAULT_PORT, \
    RESPONSE, ERROR, MESSAGE, EXIT, DESTINATION
import time

from common.variables import SENDER, MESSAGE_TEXT
from decos import log
from errors import ReqFieldMissingError, IncorrectDataRecivedError

CLIENT_LOGGER = logging.getLogger('client')

@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }

@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                           f'\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break

@log
def create_message(sock, account_name = 'Guest'):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    out_massage = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформированно сообщение серверу: {out_massage}')
    try:
        send_meccage(sock, out_massage)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')

@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_meccage(sock, create_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')

    return server_address, server_port, client_name

@log
def main():
    server_adr, server_port, client_name = arg_parser()
    print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_adr}, '
        f'порт: {server_port}, имя пользователя: {client_name}')
    try:
        transport = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        transport.connect((server_adr,server_port))
        send_meccage(transport, create_presence(client_name))
        CLIENT_LOGGER.info(f'Серверу отправлено сообщение')
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера:{answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Не удалось декодировать JSON от сервера')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_adr}:{server_port} '
                               f'Сервер отверг запрос на подключение')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутвует необходимое поле '
                            f'{missing_error.missing_field}')
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break

if __name__ == '__main__':
    main()