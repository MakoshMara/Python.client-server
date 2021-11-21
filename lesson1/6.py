# Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
import locale

import chardet
from chardet.universaldetector import UniversalDetector

def create_file(arr):
    with open('test_file.txt', 'w') as file:
        for line in arr:
            file.write(f'{line}\n')

def read_file():
    default_encoding = locale.getpreferredencoding()
    with open('test_file.txt') as file:
        if default_encoding != 'utf-8':
            for line in file:
                print(line.encode(encoding='utf-8'))




create_file(['сетевое программирование', 'сокет', 'декоратор'])
read_file()
