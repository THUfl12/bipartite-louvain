#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 20:52
# @Author  : fengliang
# @File    : bigraph.py
from .binodes import BiNode


class BiGraph(object):
    def __init__(self):
        self.__nodes__ = dict()
        self.neighbors = dict()
        self.red_to_blue_edges = dict()
        self.blue_to_red_edges = dict()

    def nodes(self):
        return list(self.__nodes__.keys())

    def build_init_bigraph(self, graph):
        for node in graph.nodes():
            self.red_to_blue_edges[node] = dict()
            self.blue_to_red_edges[node] = dict()

            if graph.nodes[node]['color'] == 'red':
                self.add_node(node, graph.degree(weight='weight')[node], 0, 0)
            else:
                self.add_node(node, 0, graph.degree(weight='weight')[node], 0)

            self.add_init_node_neighbors(graph, node)

    def add_node(self, node, red_degree, blue_degree, edge):
        self.__nodes__[node] = BiNode(red_degree, blue_degree, edge)

    def add_init_node_neighbors(self, graph, node):
        self.neighbors[node] = []
        for neigh in graph.neighbors(node):
            self.neighbors[node].append(neigh)
            self.add_init_edges(graph.nodes[neigh]['color'], node, neigh,
                                graph[node][neigh].get('weight', 1))

    def add_init_edges(self, color, source_node, end_node, weight):
        if color == 'blue':
            self.red_to_blue_edges[source_node][end_node] = weight
            self.blue_to_red_edges[source_node][end_node] = 0
        else:
            self.red_to_blue_edges[source_node][end_node] = 0
            self.blue_to_red_edges[source_node][end_node] = weight

    def get_node_info(self, node):
        self.__nodes__[node].get_info()

    def get_node_red_degree(self, node):
        return self.__nodes__[node].get_red_degree()

    def get_node_blue_degree(self, node):
        return self.__nodes__[node].get_blue_degree()

    def get_node_intra_edge(self, node):
        return self.__nodes__[node].get_intra_edge()

    def build_bigraph_partition(self, bigraph, partition):
        values = set(partition.values())
        com_nodes = {k: [] for k in values}

        for node in bigraph.nodes():
            com = partition[node]
            com_nodes[com].append(node)

        for com, nodes in com_nodes.items():
            size = len(nodes)
            if size == 1:
                node = nodes[0]
                red_degree = bigraph.get_node_red_degree(node)
                blue_degree = bigraph.get_node_blue_degree(node)
                intra_edge = bigraph.get_node_intra_edge(node)

                self.add_node(com, red_degree, blue_degree, intra_edge)
            else:
                red_degree, blue_degree, intra_edge = 0, 0, 0
                for i in range(size):
                    red_degree += bigraph.get_node_red_degree(nodes[i])
                    blue_degree += bigraph.get_node_blue_degree(nodes[i])
                    intra_edge += bigraph.get_node_intra_edge(nodes[i])
                    for j in range(i+1, size):
                        intra_edge += bigraph.red_to_blue_edges[nodes[i]].get(nodes[j], 0)
                        intra_edge += bigraph.blue_to_red_edges[nodes[i]].get(nodes[j], 0)

                self.add_node(com, red_degree, blue_degree, intra_edge)

        self.add_neighbors_inter_edges(bigraph, com_nodes, partition)

    def add_neighbors_inter_edges(self, bigraph, com_nodes, partition):
        for com, nodes in com_nodes.items():
            temp_neighbors = set()
            self.red_to_blue_edges[com] = dict()
            self.blue_to_red_edges[com] = dict()
            for node in nodes:
                node_neighbors = bigraph.neighbors[node]
                for neigh in node_neighbors:
                    neigh_com = partition[neigh]
                    if neigh_com == com:
                        continue

                    temp_neighbors.add(neigh_com)

                    self.red_to_blue_edges[com][neigh_com] = self.red_to_blue_edges[com].get(neigh_com, 0) + \
                                                             bigraph.red_to_blue_edges[node].get(neigh, 0)
                    self.blue_to_red_edges[com][neigh_com] = self.blue_to_red_edges[com].get(neigh_com, 0) + \
                                                             bigraph.blue_to_red_edges[node].get(neigh, 0)

            self.neighbors[com] = list(temp_neighbors)
