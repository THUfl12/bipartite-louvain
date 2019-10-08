#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/29 17:59
# @Author  : fengliang
# @File    : bipartite_status.py


class Status(object):
    def __init__(self):
        self.node2com = dict()
        self.total_weight = 0
        self.intra_edges = dict()
        self.red_degrees = dict()
        self.blue_degrees = dict()
        self.intra_node_edges = dict()
        self.red_node_degree = dict()
        self.blue_node_degree = dict()

    def copy(self):
        new_status = Status()
        new_status.node2com = self.node2com
        new_status.total_weight = self.total_weight
        new_status.intra_edges = self.intra_edges
        new_status.red_degrees = self.red_degrees
        new_status.blue_degrees = self.blue_degrees
        new_status.intra_node_edges = self.intra_node_edges
        new_status.red_node_degree = self.red_node_degree
        new_status.blue_node_degree = self.blue_node_degree

    def init(self, bigraph, partition=None):
        self.node2com = dict()
        self.total_weight = 0
        self.intra_edges = dict()
        self.red_degrees = dict()
        self.blue_degrees = dict()
        self.intra_node_edges = dict()
        self.red_node_degree = dict()
        self.blue_node_degree = dict()

        if partition is None:
            com = 1
            for node in bigraph.nodes():
                self.node2com[node] = com
                self.red_node_degree[node] = bigraph.get_node_red_degree(node)
                self.blue_node_degree[node] = bigraph.get_node_blue_degree(node)
                self.intra_node_edges[node] = bigraph.get_node_intra_edge(node)

                self.blue_degrees[com] = bigraph.get_node_blue_degree(node)
                self.red_degrees[com] = bigraph.get_node_red_degree(node)
                self.intra_edges[com] = bigraph.get_node_intra_edge(node)

                com += 1

            self.total_weight = sum(self.red_degrees.values())
        else:
            com_nodes = dict()
            for node in bigraph.nodes():
                com = partition[node]
                self.node2com[node] = com
                self.red_node_degree[node] = bigraph.get_node_red_degree(node)
                self.blue_node_degree[node] = bigraph.get_node_blue_degree(node)
                self.intra_node_edges[node] = bigraph.get_node_intra_edge(node)

                if com_nodes.get(com, None) is None:
                    com_nodes[com] = [node]
                else:
                    com_nodes[com].append(node)

            unique_com = set(partition.values())
            self.red_degrees = {k: 0. for k in unique_com}
            self.blue_degrees = {k: 0. for k in unique_com}
            self.intra_edges = {k: 0. for k in unique_com}

            for com, nodes in com_nodes.items():
                size = len(nodes)
                if size == 1:
                    self.blue_degrees[com] += bigraph.get_node_blue_degree(nodes[0])
                    self.red_degrees[com] += bigraph.get_node_red_degree(nodes[0])
                    self.intra_edges[com] += bigraph.get_node_intra_edge(nodes[0])
                else:
                    for i in range(size):
                        self.blue_degrees[com] += bigraph.get_node_blue_degree(nodes[i])
                        self.red_degrees[com] += bigraph.get_node_red_degree(nodes[i])
                        self.intra_edges[com] += bigraph.get_node_intra_edge(nodes[i])
                        for j in range(i+1, size):
                            self.intra_edges[com] += bigraph.red_to_blue_edges[nodes[i]].get(nodes[j], 0.)
                            self.intra_edges[com] += bigraph.blue_to_red_edges[nodes[i]].get(nodes[j], 0.)

            self.total_weight = sum(self.red_degrees.values())



