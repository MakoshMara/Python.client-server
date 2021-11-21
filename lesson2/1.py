"""
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список.
Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. '
В этой же функции создать главный список для хранения данных отчета — например,
main_data — и поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""
import csv
import re

def get_data(files):
    os_prod_list = []
    os_name_list =[]
    os_code_list = []
    os_type_list = []
    list_of_lists = [os_name_list,os_code_list,os_type_list]
    main_data = [['Изготовитель системы', 'Название ОС','Код продукта','Тип системы']]
    for file in files:
        with open (file, encoding='cp1251') as f:
            for line in f:
                if re.findall('Изготовитель системы', line) != []:
                    prod = re.findall(r'\w+',line.split(':')[1])
                    os_prod_list.append(prod)
                if re.findall('Название ОС', line) != []:
                    name = re.findall(r'\b.+', line.split(':')[1])
                    os_name_list.append(name)
                if re.findall('Код продукта', line) != []:
                    code = re.findall(r'\b.+', line.split(':')[1])
                    os_code_list.append(code)
                if re.findall('Тип системы', line) != []:
                    type = re.findall(r'\b.+', line.split(':')[1])
                    os_type_list.append(type)
    for k in os_prod_list:
        main_data.append(k)
    for list in list_of_lists:
        n = 1
        for k in list:
            main_data[n].append(k[0])
            n +=1
            print(main_data)
    return main_data

def write_to_csv(file):
    with open(file, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        data = get_data(['info_1.txt', 'info_2.txt','info_3.txt'])
        writer.writerows(data)



write_to_csv('main_data.csv')