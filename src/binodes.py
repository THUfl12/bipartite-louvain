#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 20:43
# @Author  : fengliang
# @File    : binodes.py


class BiNode(object):

    def __init__(self, red_degree, blue_degree, edge):
        self.red_degree = red_degree
        self.blue_degree = blue_degree
        self.edge = edge

    def get_red_degree(self):
        return self.red_degree

    def get_blue_degree(self):
        return self.blue_degree

    def get_intra_edge(self):
        return self.edge

    def get_info(self):
        print('red degree: %d, blue degree: %d, intra-edges: %d' %
              (self.red_degree, self.blue_degree, self.edge))
