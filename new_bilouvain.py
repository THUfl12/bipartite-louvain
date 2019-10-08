#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/29 17:39
# @Author  : fengliang
# @File    : new_bilouvain.py
import random
from .bigraph import BiGraph
from .bipartite_status import Status
__MIN = 1e-5


def partition_at_level(dendrogram, level):
    partition = dendrogram[0].copy()
    for index in range(1, level + 1):
        for node, community in partition.items():
            partition[node] = dendrogram[index][community]
    return partition


def new_bilouvain(bigraph, partition=None, randomize=True):
    status = Status()
    status.init(bigraph, partition)
    status_list = list()
    __one_level(bigraph, status, randomize)
    new_mod = __bipartite_modularity(status)
    partition = __renumber(status.node2com)
    status_list.append(partition)

    mod = new_mod
    current_graph = induced_graph(partition, bigraph)
    status.init(current_graph)

    while True:
        __one_level(current_graph, status, randomize)
        new_mod = __bipartite_modularity(status)
        if new_mod - mod < __MIN:
            break
        partition = __renumber(status.node2com)
        status_list.append(partition)
        mod = new_mod
        current_graph = induced_graph(partition, current_graph)
        status.init(current_graph)

    return mod, partition_at_level(status_list, len(status_list)-1)


def __one_level(bigraph, status, randomize):
    # print('-------------one level-------------')
    modified = True
    cur_mod = __bipartite_modularity(status)
    new_mod = cur_mod

    while modified:
        cur_mod = new_mod
        modified = False
        # print(cur_mod)

        for node in __randomly(bigraph.nodes(), randomize):
            com_node = status.node2com[node]
            red_gdegree = status.red_node_degree.get(node, 0) / status.total_weight
            blue_gdegree = status.blue_node_degree.get(node, 0) / status.total_weight
            neigh_communities, weights_rtb, weight_btr = __neighcom(node, bigraph, status)
            __remove(node, com_node, weights_rtb.get(com_node, 0), weight_btr.get(com_node, 0), status)
            best_com = com_node
            best_increase = 0

            for neigh_com in __randomly(neigh_communities, randomize):
                incr = weights_rtb[neigh_com] - status.blue_degrees.get(neigh_com, 0)*red_gdegree + \
                       weight_btr[neigh_com] - status.red_degrees.get(neigh_com, 0)*blue_gdegree

                if incr > best_increase:
                    best_increase = incr
                    best_com = neigh_com

            __insert(node, best_com, weights_rtb.get(best_com, 0), weight_btr.get(best_com, 0), status)
            if best_com != com_node:
                modified = True

        new_mod = __bipartite_modularity(status)
        if new_mod - cur_mod < __MIN:
            break


def induced_graph(partition, bigraph):
    new_bigraph = BiGraph()
    new_bigraph.build_bigraph_partition(bigraph, partition)

    return new_bigraph


def __renumber(dictionary):
    count = 0
    ret = dictionary.copy()
    new_values = dict([])

    for key in dictionary.keys():
        value = dictionary[key]
        new_value = new_values.get(value, -1)
        if new_value == -1:
            new_values[value] = count
            new_value = count
            count += 1
        ret[key] = new_value

    return ret


def __insert(node, com, weight_rtb, weight_btr, status):
    status.red_degrees[com] = status.red_degrees.get(com, 0) + status.red_node_degree.get(node, 0)
    status.blue_degrees[com] = status.blue_degrees.get(com, 0) + status.blue_node_degree.get(node, 0)

    status.intra_edges[com] = status.intra_edges.get(com) + weight_rtb + weight_btr + \
                              status.intra_node_edges.get(node, 0)

    status.node2com[node] = com


def __remove(node, com, weight_rtb, weight_btr, status):
    status.red_degrees[com] = status.red_degrees.get(com, 0) - status.red_node_degree.get(node, 0)
    status.blue_degrees[com] = status.blue_degrees.get(com, 0) - status.blue_node_degree.get(node, 0)

    status.intra_edges[com] = status.intra_edges.get(com) - weight_rtb - weight_btr - \
                              status.intra_node_edges.get(node, 0)

    status.node2com[node] = -1


def __neighcom(node, bigraph, status):
    weights_red_to_blue = {}
    weights_blue_to_red = {}
    neighbors = bigraph.neighbors[node]
    neigh_communities = set()

    for neigh in neighbors:
        neigh_com = status.node2com[neigh]
        neigh_communities.add(neigh_com)

        red_to_blue_weight = bigraph.red_to_blue_edges[node].get(neigh, 0)
        weights_red_to_blue[neigh_com] = weights_red_to_blue.get(neigh_com, 0) + red_to_blue_weight

        blue_to_red_weight = bigraph.blue_to_red_edges[node].get(neigh, 0)
        weights_blue_to_red[neigh_com] = weights_blue_to_red.get(neigh_com, 0) + blue_to_red_weight

    return neigh_communities, weights_red_to_blue, weights_blue_to_red


def __randomly(seq, randomize):
    if randomize:
        shuffled = list(seq)
        random.shuffle(shuffled)
        return iter(shuffled)
    return seq


def __bipartite_modularity(status):
    m = status.total_weight
    result = 0
    for com in set(status.node2com.values()):
        red_degree = status.red_degrees.get(com, 0)
        blue_degree = status.blue_degrees.get(com, 0)
        intra_edges = status.intra_edges.get(com, 0)

        result += intra_edges - red_degree*blue_degree/m

    result = result / m

    return result
