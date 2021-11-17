# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

def check(arr):
    n = 0
    while n < len(arr):
        for l in arr[n]:
            if ord(l)>127:
                print(f'Невозможно записать "{arr[n]}" в байтовом типе')
                break
        n+=1

check(['attribute','класс', 'функция','type'])