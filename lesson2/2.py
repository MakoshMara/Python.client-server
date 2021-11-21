"""
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в файл
orders.json. При записи данных указать величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json


def write_order_to_json(arr):
    keys = ['item', 'quantity', 'price', 'buyer', 'date']
    n = 0
    dict_for_json = {}
    for key in keys:
        dict_for_json.setdefault(key, arr[n])
        n += 1
    with open('orders.json', 'r', encoding='utf-8') as file:
        orders = json.load(file)
    with open('orders.json', 'w', encoding='utf-8') as file:
        orders['orders'].append(dict_for_json)
        print(orders['orders'])
        json.dump(orders, file, indent=4)


write_order_to_json(['Кокошник', '1', '1100', 'Внученька', '25.11.21'])
write_order_to_json(['Синяя дубленка', '1', '2000', 'Дедушка', '25.11.21'])
