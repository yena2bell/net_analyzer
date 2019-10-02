# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 23:51:55 2019

@author: jwKim
"""

import numpy as np

from . import basic_topology_functions
from ..support_functions import combination_functions

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
    print("MDS calculation. maximum calculation is ", pow(2,i_num_nodes_not_input))
    i_calculation = 0
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
        i_calculation += 1
        if i_calculation % 20000 == 0:
            print(i_calculation,"th calculation is done")
        if len(larray_MDS) == 1:
            i_num_MDS = np.count_nonzero(array_test_comb)
            
        i_test_comb = combination_functions.calculate_next_combination(i_test_comb, i_num_nodes_not_input)
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


def find_DS_directednet(ls_nodes, lt_links, i_covering_distance=1):
    
    ls_DS = []
    
    matrix_topology = np.array(basic_topology_functions.convert_net_topology_from_basic_to_matrix(ls_nodes,lt_links))
    matrix_topology_with_selfloop = matrix_topology + np.identity(len(ls_nodes), dtype=int)
    
    matrix_covering_in_distance = np.identity(len(ls_nodes))
    for _ in range(i_covering_distance):
        matrix_covering_in_distance = np.matmul(matrix_covering_in_distance, matrix_topology_with_selfloop)
    
    #DS always contain input nodes
    ls_nodes_input = basic_topology_functions.find_input_nodes(ls_nodes, lt_links)
    ls_DS.extend(ls_nodes_input)
    
    set_covered = set([])
    for s_node in ls_nodes_input:
        li_node_covered = list(matrix_covering_in_distance[:,ls_nodes.index(s_node)].nonzero()[0])
        set_covered.update(li_node_covered)
        for i_node in li_node_covered:
            matrix_covering_in_distance[i_node] = 0
    
    while len(set_covered) < len(ls_nodes):
        i_node_to_select = None
        i_num_of_covered_by_selected = 0
        li_nodes_covered_by_selected = []
        for i_node in (ls_nodes.index(s_node) for s_node in ls_nodes if s_node not in ls_DS):
            l_tmp = list(matrix_covering_in_distance[:,i_node].nonzero()[0])
            if len(l_tmp) > i_num_of_covered_by_selected:
                i_node_to_select = i_node
                i_num_of_covered_by_selected = len(l_tmp)
                li_nodes_covered_by_selected = l_tmp
        ls_DS.append(ls_nodes[i_node_to_select])
        set_covered.update(li_nodes_covered_by_selected)
        for i_node_covered in li_nodes_covered_by_selected:
            matrix_covering_in_distance[i_node_covered] = 0
    
    return ls_DS

def find_MDS_directednet_reversely(ls_nodes, lt_links, i_covering_distance=1):
    ls_DS = find_DS_directednet(ls_nodes, lt_links, i_covering_distance=1)
    
    array_topology = np.array(basic_topology_functions.convert_net_topology_from_basic_to_matrix(ls_nodes,lt_links))
    array_topology_with_selfloop = array_topology + np.identity(len(ls_nodes), dtype=int)
    
    matrix_cover_relation_in_distance = np.identity(len(ls_nodes), dtype=int)
    for _ in range(i_covering_distance):
        matrix_covering_in_distance = np.matmul(matrix_cover_relation_in_distance, array_topology_with_selfloop)
    
    i_num_MDS = len(ls_DS)#it will be changed after find MDS
    larray_MDS = []
    
    #MDS always contain input nodes
    ls_nodes_input = basic_topology_functions.find_input_nodes(ls_nodes, lt_links)
    li_index_nodes_input = [ls_nodes.index(s_node) for s_node in ls_nodes_input]
    li_index_nodes_input.sort()
    print("the number of input nodes is ", len(li_index_nodes_input))
    
    i_num_nodes_not_input = len(ls_nodes) - len(li_index_nodes_input)
    i_calculation = 0

    i_num_covered_except_inputs = i_num_MDS-len(li_index_nodes_input)
    print("combinations with ",i_num_covered_except_inputs-1," nodes covered are now calculating")
    for i_combination in combination_functions.generator_combination_num_in_defined_1(i_num_nodes_not_input, i_num_covered_except_inputs-1):
        s_combination = ("{0:0%db}"%i_num_nodes_not_input).format(i_combination)
        l_combination = list(s_combination)
        for i_index in li_index_nodes_input:
            l_combination.insert(i_index,1)
        array_combination = np.array(l_combination,dtype=int)
        array_covered = np.matmul(matrix_covering_in_distance, array_combination)
        if np.all(array_covered):
            larray_MDS.append(array_combination)
        i_calculation += 1
        if i_calculation % 20000 == 0:
            print(i_calculation,"th calculation is done")
        
    if len(larray_MDS) == 0:
        #the number of MDS nodes is same as the number of DS nodes.
        print("combinations with ",i_num_covered_except_inputs," nodes covered are now calculating")
        for i_combination in combination_functions.generator_combination_num_in_defined_1(i_num_nodes_not_input, i_num_covered_except_inputs):
            s_combination = ("{0:0%db}"%i_num_nodes_not_input).format(i_combination)
            l_combination = list(s_combination)
            for i_index in li_index_nodes_input:
                l_combination.insert(i_index,1)
            array_combination = np.array(l_combination,dtype=int)
            array_covered = np.matmul(matrix_covering_in_distance, array_combination)
            if np.all(array_covered):
                larray_MDS.append(array_combination)
            i_calculation += 1
            if i_calculation % 20000 == 0:
                print(i_calculation,"th calculation is done")
        lls_MDS = []
        for array_MDS in larray_MDS:
            ls_MDS = [ls_nodes[i] for i in np.nonzero(array_MDS)[0]]
            lls_MDS.append(ls_MDS)
        return lls_MDS
    else:
        
        while larray_MDS:
            larray_MDS_before= larray_MDS.copy()
            larray_MDS = []
            i_num_covered_except_inputs -= 1
            print("combinations with ",i_num_covered_except_inputs," nodes covered are now calculating")
            for i_combination in combination_functions.generator_combination_num_in_defined_1(i_num_nodes_not_input, i_num_covered_except_inputs):
                s_combination = ("{0:0%db}"%i_num_nodes_not_input).format(i_combination)
                l_combination = list(s_combination)
                for i_index in li_index_nodes_input:
                    l_combination.insert(i_index,1)
                array_combination = np.array(l_combination,dtype=int)
                array_covered = np.matmul(matrix_covering_in_distance, array_combination)
                if np.all(array_covered):
                    larray_MDS.append(array_combination)
                i_calculation += 1
                if i_calculation % 20000 == 0:
                    print(i_calculation,"th calculation is done")
        
        for array_MDS in larray_MDS_before:
            ls_MDS = [ls_nodes[i] for i in np.nonzero(array_MDS)[0]]
            lls_MDS.append(ls_MDS)
        return lls_MDS
