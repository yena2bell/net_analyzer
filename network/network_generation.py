# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 23:26:50 2019

@author: jwKim
"""
import numpy as np



def gen_network_scale_free_out(node_num=20, a=2):
    """this function was made by modifing Jail's code"""

    # if a = 2 pareto shape, mean = 2.0 with mode = 1
    while 1:
        out_degree = np.random.pareto(a, node_num)
        array_out_degree = np.array([int(f) + 1 for f in out_degree])
        if all(array_out_degree < node_num):
            break
    l_snodenames = [str(i) for i in range(node_num)]
    l_t_edges = []
    for s_source in l_snodenames:
        seq = l_snodenames[:]
        seq.remove(s_source)
        targets = np.random.choice(seq,array_out_degree[l_snodenames.index(s_source)],replace=False)
        l_t_edges += list(zip([s_source]*len(targets),targets))
        
    return l_snodenames, l_t_edges


def gen_network_scalefree_connected(i_nodenum, i_a):
    b_flag_connected = False
    while not b_flag_connected:
        nx_network, b_flag_connected = gen_network_scale_free_out(i_nodenum, i_a)
    
    return nx_network