# Выполнить пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовать результаты из байтовового в строковый тип на кириллице.

import subprocess
import chardet

ARGS = [['ping', 'yandex.ru', '-n', '6'], ['ping', 'youtube.com', '-n', '6']]
for arg in ARGS:
    YA_PING = subprocess.Popen(arg, stdout=subprocess.PIPE)
    for line in YA_PING.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))