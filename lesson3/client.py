import logging
import sys
import socket
import json
import logs.config_client_log

from lesson3.common.utils import send_meccage, get_message
from lesson3.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, DEFAULT_IP_ADRESS, DEFAULT_PORT, \
    RESPONSE, ERROR
import time

from decos import log
from lesson3.errors import ReqFieldMissingError

CLIENT_LOGGER = logging.getLogger('client')

@log
def create_presence(account_name = 'Guest'):
    out_massage = {
        ACTION:PRESENCE,
        TIME:time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформированно сообщение серверу: {out_massage}')
    return out_massage

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
def main():
    try:
        server_adr = sys.argv[1]
        server_port = sys.argv[2]
        if server_port <1024 or server_port> 65535:
            raise ValueError
    except IndexError:
        server_adr = DEFAULT_IP_ADRESS
        server_port = DEFAULT_PORT
        CLIENT_LOGGER.info(f'При запуске клиента не введен номер порта или адрес после соотвествующих параметров')
    except ValueError:
        CLIENT_LOGGER.error(f'Номер порта не может быть меньше 1024 или больше 65565')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: '
                       f'Адрес сервера: {server_adr} '
                       f'Порт сервера: {server_port}')

    transport = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    transport.connect((server_adr,server_port))
    message_to_server = create_presence()
    CLIENT_LOGGER.info(f'Серверу отправлено сообщение')
    send_meccage(transport, message_to_server)
    try:
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера:{answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Не удалось декодировать JSON от сервера')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_adr}:{server_port}'
                               f'Сервер отверг запрос на подключение')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутвует необходимое поле '
                            f'{missing_error.missing_field}')

if __name__ == '__main__':
    main()