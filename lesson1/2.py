# Каждое из слов «class», «function», «method» записать в байтовом типе
# без преобразования в последовательность кодов (не используя методы encode и decode)
# и определить тип, содержимое и длину соответствующих переменных.

def to_bytes(arr):
    for word in arr:
        res = eval(f'b"{word}"')
        print(res)
        print(type(res))
        print(len(res))


to_bytes(['class', 'function', 'method'])

