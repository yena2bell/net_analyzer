# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 23:51:55 2019

@author: jwKim
"""

import numpy as np

from . import basic_topology_functions

def find_MDS_directednet(ls_nodes, lt_links, i_covering_distance=1):
    """find MDS nodes of the network.
    return list of MDS nodes list.
    every node of network are either MDS node or downstream node of some MDS node within distance i_covering_distance"""
    array_topology = np.array(basic_topology_functions.convert_net_topology_from_basic_to_matrix(ls_nodes,lt_links))
    array_topology_with_selfloop = array_topology + np.identity(len(ls_nodes), dtype=int)
    i_num_MDS = len(ls_nodes)#it will be changed after find MDS
    larray_MDS = []
    
    #MDS always contain input nodes
    ls_nodes_input = basic_topology_functions.find_input_nodes(ls_nodes, lt_links)
    li_index_nodes_input = [ls_nodes.index(s_node) for s_node in ls_nodes_input]
    li_index_nodes_input.sort()
    
    i_num_nodes_not_input = len(ls_nodes) - len(li_index_nodes_input)
    
    i_test_comb = 0          
    s_test_comb = ("{0:0%db}"%i_num_nodes_not_input).format(i_test_comb)
    l_test_comb = list(s_test_comb)
    for i_index in li_index_nodes_input:
        l_test_comb.insert(i_index,1)
    array_test_comb = np.array(l_test_comb,dtype=int)
    
    while np.count_nonzero(array_test_comb) <= i_num_MDS:
        array_covered = array_test_comb
        for _ in range(i_covering_distance):
            array_covered = np.dot(array_topology_with_selfloop, array_covered)
        if np.all(array_covered):
            larray_MDS.append(array_test_comb)
        if len(larray_MDS) == 1:
            i_num_MDS = np.count_nonzero(array_test_comb)
            
        i_test_comb = calculate_next_combination(i_test_comb, i_num_nodes_not_input)
        s_test_comb = ("{0:0%db}"%i_num_nodes_not_input).format(i_test_comb)
        l_test_comb = list(s_test_comb)
        for i_index in li_index_nodes_input:
            l_test_comb.insert(i_index,1)
        array_test_comb = np.array(l_test_comb, dtype=int)
    
    lls_MDS = []
    for array_MDS in larray_MDS:
        ls_MDS = [ls_nodes[i] for i in np.nonzero(array_MDS)[0]]
        lls_MDS.append(ls_MDS)
    
    return lls_MDS
    
    
def find_cover_of_node_in_defined_distance(s_node, dic_startnode_setendnodes, i_distance):
    """without selfloop, result does not contain start node"""
    i_distance -= 1
    set_coverednodes_1distance = set([])
    set_coverednodes_1distance.update(dic_startnode_setendnodes[s_node])
    set_newcovered = set([])
    if i_distance:
        for s_node_1dist in set_coverednodes_1distance:
            set_newcovered.update(find_cover_of_node_in_defined_distance(s_node_1dist, dic_startnode_setendnodes, i_distance))
    
    return set_coverednodes_1distance.union(set_newcovered)
            

def calculate_next_combination(x,n):
    """
    for integer x, return integer iNext
    when x is described by binary form, x has i number of 1s.
    iNext is the smallest integer which is bigger than x and can be described by binary form using i number of 1s.
    if integer satisfying conditions is bigger than (2^n)-1, then iNext is the integer which can be described by binary form using i+1 num of 1s.
    for example, x = 100, x == 1100100(2). then iNext == 1101000(2) == 104
    """
    if n == 0:
        return False
    if x == 0:
        return(1)
 
    i_position_of_smallest_1 = 0
    i_position_of_smallest_0_after_first_1 = 0
    i_next = x
 
    while x%2 == 0:
        i_position_of_smallest_1 += 1
        x = x >> 1
    x = x >> 1
 
    while x%2 == 1:
        x = x >> 1
        i_next += pow(2,i_position_of_smallest_0_after_first_1) 
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1)
        i_position_of_smallest_0_after_first_1 += 1
 
    if i_position_of_smallest_0_after_first_1 == n-1:
        #"every combinations are found"
        return False
    elif i_position_of_smallest_0_after_first_1 > n-1:
        #"it is over the combination range"
        return False
 
    if i_position_of_smallest_1 + i_position_of_smallest_0_after_first_1 == n-1:
        #"one combination ended"
        i_next += pow(2,i_position_of_smallest_0_after_first_1) 
        i_next += pow(2,i_position_of_smallest_0_after_first_1 +1) 
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1)
    else:
        i_next -= pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1) 
        i_next += pow(2,i_position_of_smallest_1+i_position_of_smallest_0_after_first_1+1)

    """
    #test code
    z=iNext
    k = ''
    while z:
        k+=str(z%2)
        z=z>>1
    print(k)
    """
    return i_next