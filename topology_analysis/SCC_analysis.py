# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 17:34:38 2019

@author: jwKim
"""

def evaluate_SCC_inclusion(l_t_cycles,t_newcycle):
    """
    sub function of 'find_SCC_under_startnode'
    l_t_cycles = [(3,8),(11, 20) ....] 
    if l_t_cycles is [(a,b), (c,d)...] then a,b,c,d satisfy a<b<c<d 
    t_newcycle = (50, 78) this means that node 50, node51.... node 78 is SCC
    t_newcycle[1] is always bigger than l_t_cycles[-1][1].
    tCycle is the record of feedback in the flow. if tCycle==(a,b) then a<b
    this function input t_newcycle to l_t_cycles and arrange l_t_cycles
    """

    for t_cycle in l_t_cycles:
        if t_cycle[1] < t_newcycle[0]:
            continue #tCycle has no common nodes with tNewCycle. so go to next cycle
        elif t_cycle[0] <= t_newcycle[0]: #satisfy t_cycle[1] >= t_newcycle[0]
            t_newcycle = (t_cycle[0],t_newcycle[1])
            i_posi_of_t_cycle = l_t_cycles.index(t_cycle) 
            break
        else: #tCycle[0]>tNewCycle
            i_posi_of_t_cycle = l_t_cycles.index(t_cycle)
            break
    else:
        l_t_cycles.append(t_newcycle)
        return l_t_cycles

    l_t_cycles = l_t_cycles[0:i_posi_of_t_cycle]
    l_t_cycles.append(t_newcycle)
    return l_t_cycles



def find_SCC_under_startnode(s_node_start, l_remained_nodes, dic_startnode_setlinks):
    """
    sub function of 'decompose_SCC'
    nodes data = [node name1, node name2, ..... node name k]
    remained nodes set don't contain start node
    dic_startnode_setlinks has node name as key and set containing edges starting that node as value
    SCC is the form of [node1,node2,,,]
    """

    l_node_flow = [s_node_start]
    ll_SCC = []
    l_t_cycle_positions = []

    while l_node_flow:
        #print("\ntest2",len(l_node_flow))
        #time.sleep(0.5)
        #for node_test in l_node_flow:
        #    print(node_test.output_name(), end = ',')
        
        if not dic_startnode_setlinks[s_node_start]:#dic_startnode_setlinks[s_node_start] is empty set
            i_posi_of_node = l_node_flow.index(s_node_start)
            if not(l_t_cycle_positions):# there is no feedback in the flow
                ll_SCC.append([l_node_flow.pop(-1)])
            elif l_t_cycle_positions[-1][1] < i_posi_of_node:# end node of the flow is sink node
                ll_SCC.append([l_node_flow.pop(-1)])
            elif i_posi_of_node == l_t_cycle_positions[-1][0]:
                t_SCC = l_t_cycle_positions.pop(-1)
                ll_SCC.append(l_node_flow[t_SCC[0]:t_SCC[1]+1])
                l_node_flow = l_node_flow[:t_SCC[0]]
            elif l_node_flow:
                s_node_start = l_node_flow[l_node_flow.index(s_node_start)-1]
                continue
            
            if l_node_flow:
                s_node_start = l_node_flow[-1] 
            continue
        
        t_link_selected = dic_startnode_setlinks[s_node_start].pop()
        s_node_next = t_link_selected[1]
        if s_node_next in l_node_flow:
            t_cycle = (l_node_flow.index(s_node_next), len(l_node_flow)-1)
            l_t_cycle_positions = evaluate_SCC_inclusion(l_t_cycle_positions,t_cycle)
        elif s_node_next in l_remained_nodes:
            l_node_flow.append(s_node_next)
            l_remained_nodes.pop(l_remained_nodes.index(s_node_next))
            s_node_start = s_node_next
        
    return ll_SCC


def decompose_SCC(l_nodes, lt_links_data):
    """
    l_nodes_data = [node name1, node name2, ..... node name k] node name should be string
    lt_links_data = [(node name1, node name2), (node name1, node name3)...]
    (node1, node2) means node1 interacte to node2 i.e. node1 -> node2
    """    
    #copy the list data to conserve original data
    l_remained_nodes = l_nodes.copy()    
    print("the number of nodes to analyze is", len(l_remained_nodes))
    dic_startnode_setlinks = {}
    ll_SCC = []
    
    for t_link in lt_links_data:
        dic_startnode_setlinks.setdefault(t_link[0],set([])).add(t_link)

    while(l_remained_nodes):
        ll_SCC += find_SCC_under_startnode(l_remained_nodes.pop(0), l_remained_nodes, dic_startnode_setlinks)
        """
        choose one node and make it start node.
        find SCC containing that start node and SCC whose hierarchy is lower than SCC containing start node
        repeat until find all SCCs
        """

    return ll_SCC


def is_SCC1_over_SCC2(SCC1, SCC2):
    """
    SCC is form of [node1, node2,,,,]
    if SCC1 has node which has outward links connected nodes of SCC2
    then return True, else return False
    """
    for node in SCC1:
        for link in node.output_outward_links():
            if link.output_end() in SCC2:
                return True
    return False