#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 22:40
# @Author  : fengliang
# @File    : test_southern_women.py

import pandas as pd
import networkx as nx
from time import time
from src.new_bilouvain import new_bilouvain
from src.bigraph import BiGraph
from networkx.algorithms import bipartite
import numpy as np

file = '../data/southern_women/edges.txt'

df = pd.read_csv(file, header=None, sep=' ')
df.columns = ['women', 'event']

women_list = df['women'].tolist()
event_list = df['event'].tolist()

women_number = len(set(women_list))
event_number = len(set(event_list))

G = nx.Graph()

unique_women = sorted(set(women_list))
unique_event = sorted(set(event_list))
unique_event = [i+women_number for i in unique_event]

G.add_nodes_from(unique_women, color='red')
G.add_nodes_from(unique_event, color='blue')

for i in range(len(women_list)):
    G.add_edge(women_list[i], event_list[i]+women_number)

adjacent_matrix = bipartite.biadjacency_matrix(G, unique_women, unique_event)
bi_adjacent = adjacent_matrix.todense()

file_mat = 'data.txt'
np.savetxt(file_mat, bi_adjacent, fmt='%d', delimiter=' ')

epochs = 20
start_time = time()

bigraph = BiGraph()
bigraph.build_init_bigraph(G)

bimodularity_list = []
for i in range(epochs):
    bimodularity, partition = new_bilouvain(bigraph)
    print(len(set(partition.values())), bimodularity)

print('%d round, consume time: %.3f seconds' % (epochs, time() - start_time))


