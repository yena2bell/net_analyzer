# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 23:26:50 2019

@author: jwKim
"""
import numpy as np
import random



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


def gen_modalities_to_network(l_edges, f_probability_activation=0.5):
    """f_probability_activation is the probability of madality activation (True)"""
    i_num_edges = len(l_edges)
    array_modalities = np.random.rand(i_num_edges)<f_probability_activation#True->activation, False-> repression
    dic_t_edge_b_modality = {l_edges[i]:array_modalities[i] for i in range(i_num_edges)}
    
    return dic_t_edge_b_modality


def get_random_Boolean_logic_table_node(l_ordered_inputs, dic_predecessor_b_modality=None):
    """ for input (a,b,c), i_table means
    a,b,c output    i_table = sum(in*pow(2,n))
    0,0,0   i0
    0,0,1   i1
    0,1,0   i2
    0,1,1   i3
    1,0,0   i4
    1,0,1   i5
    1,1,0   i6
    1,1,1   i7
    filtering logic which contains meaningless input node"""
    i_numinteraction = len(l_ordered_inputs)
    if i_numinteraction == 0:#input nodes
        return None
    i_max_value_table = pow(2,pow(2,i_numinteraction))-1
    b_flag_all_interactions_are_meaningfull = False
    b_flag_modality_condition = False
    
    if dic_predecessor_b_modality:
        while not (b_flag_all_interactions_are_meaningfull and b_flag_modality_condition):
            i_table = random.randint(1,i_max_value_table)#0 and i_max_value_table is meaningless logic
            b_flag_all_interactions_are_meaningfull = check_meaningless_interaction(i_table, i_numinteraction)
            b_flag_modality_condition = check_modality_condition(i_table, dic_predecessor_b_modality, l_ordered_inputs)
            
    else:
        while not b_flag_all_interactions_are_meaningfull:
            i_table = random.randint(1,i_max_value_table)#0 and i_max_value_table is meaningless logic
            b_flag_all_interactions_are_meaningfull = check_meaningless_interaction(i_table, i_numinteraction)
            
    
    return i_table


def check_meaningless_interaction(i_Booleantable, i_numinteraction):
    """return False if some links are meaningless
    so, choose i_Booleantable have the function value True"""
    i_numtableline = pow(2,i_numinteraction)
    b_flag_meaningless_logic = True
    for i in range(i_numinteraction):
        j = 0
        i_interval = pow(2,i)
        k = j+i_interval
        b_flag_meaningless_interaction = True #it should be changed to False.
        while k < i_numtableline and b_flag_meaningless_interaction:
            b_jthline = (i_Booleantable>>j)%2
            b_kthline = (i_Booleantable>>k)%2
            b_flag_meaningless_interaction = b_flag_meaningless_interaction and (b_jthline == b_kthline)
            if (k+1) % pow(2,i+1) == 0:
                j = k+1
                k = j+i_interval
            else:
                j += 1
                k += 1
        #if ith interaction have meaning, then b_flag_meaningless_interacion == False
        b_flag_meaningless_logic = b_flag_meaningless_logic and not b_flag_meaningless_interaction
        
    return b_flag_meaningless_logic


def check_modality_condition(i_Booleantable, dic_predecessor_b_modality, l_order_of_input):
    """dic_i_predecessor_b_modality {i, True or false}
    if j th node is checked, i->j should be activation if dic_i_predecessor_b_modality[i] == True
    i->j should be suppression if dic_i_predecessor_b_modality[i] == False"""
    i_numinteraction = len(l_order_of_input)
    i_numtableline = pow(2,i_numinteraction)
    b_flag_modality_satisfying_logic = True
    for i in range(i_numinteraction):
        j = 0
        i_interval = pow(2,i)
        k = j+i_interval
        b_flag_modality_satisfying_interaction = True
        while k < i_numtableline and b_flag_modality_satisfying_interaction:
            b_jthline = (i_Booleantable>>j)%2#l_order_of_input[i_numinteraction-i-1] has value 0
            b_kthline = (i_Booleantable>>k)%2#l_order_of_input[i_numinteraction-i-1] has value 1
            if dic_predecessor_b_modality[l_order_of_input[i_numinteraction-i-1]]: #True: activation 
                if b_jthline and not b_kthline:
                    b_flag_modality_satisfying_interaction = False
            else:#b_modality == False: inhibition
                if b_kthline and not b_jthline:
                    b_flag_modality_satisfying_interaction = False
            if (k+1) % pow(2,i+1) == 0:
                j = k+1
                k = j+i_interval
            else:
                j += 1
                k += 1
        #if ith interaction have meaning, then b_flag_meaningless_interacion == False
        b_flag_modality_satisfying_logic = b_flag_modality_satisfying_logic and b_flag_modality_satisfying_interaction
    
    return b_flag_modality_satisfying_logic