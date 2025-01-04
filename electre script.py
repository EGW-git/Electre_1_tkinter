import electregui as tk
from decimal import Decimal
import operator
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
# alternatives = np.array([
#         [1, 3, 2, 1],
#         [2, 3, 1, 1],
#         [2, 2, 2, 1],
#         [3, 2, 2, 0],
#         [3, 2, 1, 1],
#         [3, 1, 2, 1],
#         [5, 1, 1, 0]
# ])
def to_str(var):
    return str(list(np.reshape(np.asarray(var), (1, np.size(var)))[0]))[1:-1]

alternatives = []
alt_len = int(input('Введите количество строк матрицы '))
for x in range(alt_len):
    alternatives.append(list(map(float, input(f"Введите значения {x+1} строки через пробел ").split())))

weights = list(map(float,input(f'Введите значения веса критериев через пробел ').split()))
alternatives = np.array(alternatives)
n = len(alternatives)
concordance_matrix = [] # Инициализация матрицы согласия

for i in range(n):  # 1 alt
    concordance_matrix.append([])
    for j in range(n):  # 2 alt
        if i == j:
            concordance_matrix[i].append(0)  # conc = 0
            continue
        concordance_index = 0
        equal_index = 0
        for k in range(len(weights)):  # Индекс критерия
            if alternatives[i][k] > alternatives[j][k]:  # Проверка i > j по k
                concordance_index += weights[k]
            elif alternatives[i][k] == alternatives[j][k]:  # Проверка i == j по k
                equal_index += weights[k]
        s = concordance_index + 0.5 * equal_index  # Вычисление индекса согласия
        concordance_matrix[i].append(Decimal(s).quantize(Decimal("1.00")))  # Добавление индекса согласия в матрицу

# print(np.array(concordance_matrix))
dis_weights = list(map(float,input(f'Введите значения веса несогласия критериев через пробел ').split()))
discordance_matrix = np.zeros((n, n)) # Инициализация матрицы несогласия

for i in range(n):
    for j in range(n):
        if i == j:
            continue
        r_max = 0
        for k in range(len(dis_weights)):
            if alternatives[j][k] > alternatives[i][k]:
                difference = alternatives[j][k] - alternatives[i][k]  # Разница ступеней
                r = difference * dis_weights[k]  # Вычисление индекса несогласия по критерию
                if r > r_max:
                    r_max = r
                if r_max > 0:
                    discordance_matrix[i][j] = max(r_max, r)

# print(discordance_matrix)
G = nx.DiGraph()  # Инициализация графа
ts_conc = float(input('Введите трешхолд для индекса согласия '))
ts_disc = float(input('Введите значение трешхолда для индекса несогласия '))
for i in range(len(concordance_matrix)): #добавление ребер с названиями в граф при заданных условиях
    for j in range(len(concordance_matrix)):
        if concordance_matrix[i][j] >= ts_conc and discordance_matrix[i][j] <= ts_disc:
            G.add_edge(f"A{i+1}", f"A{j+1}")#, labels = {i+1})

pr = nx.pagerank(G)
sort = sorted(pr.items(), key=operator.itemgetter(1), reverse=True)

# conc_m = []
# for i in range(n):
#     for j in range(n):
#         conc_m.append(str(concordance_matrix[i][j])) # convert to str
#
# for i in range(len(conc_m)):
#     if i == n:
#         conc_m.insert(i, '\n')

variables = [discordance_matrix, ''.join(str(concordance_matrix)), sort]
write_res = open("Result.txt", 'w')
for ln in variables:
    write_res.write(str(ln))
    write_res.write('\n')
write_res.close()

plt.figure(figsize=(9, 7))
pos = nx.circular_layout(G)  # Макет для расположения узлов
nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2500,
        node_color="skyblue",
        font_size=12,
        arrows=True,
        arrowsize = 16,
        width = 1.5
        )
plt.show()

