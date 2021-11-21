# Преобразовать слова «разработка», «администрирование», «protocol», «standard»
# из строкового представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).
def enc(arr):
    res_enc = []
    for word in arr:
        res_enc.append(word.encode('utf-8'))
    return res_enc
def dec(arr):
    res_dec = []
    for word in arr:
        res_dec.append(word.decode('utf-8'))
    return res_dec
print(enc(['разработка', 'администрирование', 'protocol', 'standard']))
print(dec(enc(['разработка', 'администрирование', 'protocol', 'standard'])))
