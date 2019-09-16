# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:45:55 2019

@author: jwKim
"""
import copy

def convert_net_topology_from_basic_to_matrix(ls_nodes, lt_links):
    """convert [s_node1, s_node2,,,] and [(startnode, endnode),,,] form to 
    matrix A such that Aij = 1 means (jth node, ith node) link exist"""
    ll_matrix = []
    lt_tmp_links = copy.deepcopy(lt_links)
    i_num_of_nodes = len(ls_nodes)
    for i, s_node in enumerate(ls_nodes):
        ll_matrix.append([0]*i_num_of_nodes)
        for k in range(len(lt_tmp_links)-1, -1, -1):
            if lt_tmp_links[k][1] == s_node:
                s_startnode = lt_tmp_links.pop(k)[0]
                ll_matrix[i][ls_nodes.index(s_startnode)] += 1
    
    return ll_matrix

def find_input_nodes(ls_nodes, lt_links):
    """find input(source) nodes and return the node names as list"""
    sets_nodes_not_input = set([])
    for t_link in lt_links:
        sets_nodes_not_input.add(t_link[1])
    
    sets_nodes_input = set(ls_nodes).difference(sets_nodes_not_input)
    return list(sets_nodes_input)


def split_nodes_to_source_sink(ls_nodes_to_split, ls_nodes, lt_links):
    """modify a network by spliting some nodes to sink node and source node.
    source node of the splited node has name "nodename_source" and only has outgoing links of the original node
    sink node has same property vice versa"""
    ls_nodes_new = []
    lt_links_new = []
    for s_node in ls_nodes:
        if s_node in ls_nodes_to_split:
            ls_nodes_new.append(s_node+"_source")
            ls_nodes_new.append(s_node+"_sink")
        else:
            ls_nodes_new.append(s_node)
    
    for t_link in lt_links:
        if (t_link[0] in ls_nodes_to_split) and (t_link[1] in ls_nodes_to_split):
            t_link_new = (t_link[0]+"_source", t_link[1]+"_sink")
        elif t_link[0] in ls_nodes_to_split:
            t_link_new = (t_link[0]+"_source", t_link[1])
        elif t_link[1] in ls_nodes_to_split:
            t_link_new = (t_link[0], t_link[1]+"_sink")
        else:
            t_link_new = copy.deepcopy(t_link)
        lt_links_new.append(t_link_new)
    
    return ls_nodes_new, lt_links_new


def extract_subnet_topology(lt_links, ls_nodes_sub):
    """return lt_links_sub. this is list of links(tuple form) which are elements of lt_links.
    link of lt_links_sub connect nodes only within ls_nodes_sub"""
    lt_links_sub = []
    set_nodes_sub = set(ls_nodes_sub)
    for t_link in lt_links:
        if (t_link[0] in set_nodes_sub) and (t_link[-1] in set_nodes_sub):
            lt_links_sub.append(copy.deepcopy(t_link))
    
    return lt_links_sub

def show_connected_components(ls_nodes, lt_links):
    ls_nodes_copy = ls_nodes.copy()
    l_stack = []
    lt_links_copy = lt_links.copy()
    lset_components = []
    
    while ls_nodes_copy:
        s_node = ls_nodes_copy.pop()
        set_component = set([])
        l_stack.append(s_node)
        while l_stack:
            s_node = l_stack.pop()
            set_component.add(s_node)
            for i in range(len(lt_links_copy)-1,-1,-1):
                if (lt_links_copy[i][0] == s_node):
                    t_link = lt_links_copy.pop(i)
                    if t_link[1] in ls_nodes_copy:
                        l_stack.append(ls_nodes_copy.pop(ls_nodes_copy.index(t_link[1])))
                elif (lt_links_copy[i][1] == s_node):
                    t_link = lt_links_copy.pop(i)
                    if t_link[0] in ls_nodes_copy:
                        l_stack.append(ls_nodes_copy.pop(ls_nodes_copy.index(t_link[0])))
        lset_components.append(set_component)
    
    return lset_components
        
        