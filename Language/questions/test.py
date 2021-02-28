

idfs = [
    ['number 1', 0.8, 6],
    ['number 2', 0.8, 5],
    ['number 3', 0.7, 100],
]

for key, mwm, qtd in sorted(idfs, key = lambda item: (item[1], item[2]), reverse=True):
    print(key)