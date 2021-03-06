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



def find_SCC_under_startnode_old(s_node_start, l_remained_nodes, dic_startnode_setlinks):
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


def find_SCC_under_startnode(s_node_start, l_remained_nodes, dic_startnode_setlinks):
    """
    sub function of 'decompose_SCC'
    nodes data = [node name1, node name2, ..... node name k]
    remained nodes set don't contain start node
    dic_startnode_setlinks has node name as key and set containing edges starting that node as value
    SCC is the form of [node1,node2,,,]
    """
    # get idea of upgrading code from https://github.com/qpwo/python-simple-cycles/blob/master/johnson.py
    # that codes uses Tarjan's algorithm for finding SCC's
    # Robert Tarjan. "Depth-first search and linear graph algorithms." SIAM journal on computing. 1972.

    l_node_flow = [s_node_start]
    ll_SCC = []
    i_index = 0
    i_position = 0
    dic_node_index = {s_node_start:i_index} #position of node in l_node_flow
    dic_node_lowlink = {s_node_start:i_index} #{'a':i} : i is the loweset position of node in l_node_flow among nodes connected to 'a' node.
    

    while l_node_flow:
        #print("\ntest2",len(l_node_flow))
        #time.sleep(0.5)
        #for node_test in l_node_flow:
        #    print(node_test.output_name(), end = ',')
        
        if not dic_startnode_setlinks[s_node_start]:#dic_startnode_setlinks[s_node_start] is empty set
            if dic_node_index[s_node_start] == dic_node_lowlink[s_node_start]:#it means that s_node_start has no link to node with smaller index
                ll_SCC.append(l_node_flow[i_position:])
                l_node_flow = l_node_flow[:i_position]
                if l_node_flow:
                    s_node_start = l_node_flow[-1]
                    i_position = len(l_node_flow)-1
            else:
                i_lowlink = dic_node_lowlink[s_node_start]
                s_node_start = l_node_flow[i_position-1]
                i_position -= 1
                dic_node_lowlink[s_node_start] = min(dic_node_lowlink[s_node_start], i_lowlink)            
            
        else:
            t_link_selected = dic_startnode_setlinks[s_node_start].pop()
            s_node_next = t_link_selected[1]
            if s_node_next in l_node_flow:
                dic_node_lowlink[s_node_start] = min(dic_node_lowlink[s_node_start], dic_node_index[s_node_next])
            elif s_node_next in l_remained_nodes:
                i_index += 1
                l_node_flow.append(s_node_next)
                dic_node_index[s_node_next] = i_index
                dic_node_lowlink[s_node_next] = i_index
                l_remained_nodes.pop(l_remained_nodes.index(s_node_next))
                s_node_start = s_node_next
                i_position = len(l_node_flow)-1
        
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
    
    for s_node in l_remained_nodes:
        dic_startnode_setlinks[s_node] = set([])
    
    for t_link in lt_links_data:
        dic_startnode_setlinks[t_link[0]].add(t_link)

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


def net_of_SCCs(ll_SCC, lt_links):
    """
    llSCC = [[node1,node2,node3... nodes in the SCC1],[node6,node7.... nodes in the SCC2],....]
    ltLinks_data = [(node1, node2), (node1, node3)...]
    give each SCC the number as llSCC.index
    calculate interactions between SCCs.
    return the list [(SCC1's number,SCC2's number),...] this means that link connecting SCC1 -> SCC2 exists
    """
    l_remained_links = list(lt_links)
    lt_SCClinks = []
    
    for i_lSCC in enumerate(ll_SCC):
        for i in range(len(l_remained_links)-1,-1,-1):
            if l_remained_links[i][0] in i_lSCC[1]:
                if l_remained_links[i][1] in i_lSCC[1]:
                    l_remained_links.pop(i)
                else:
                    t_tmplink = l_remained_links.pop(i)
                    t_SCClink = (i_lSCC[0],node_position_finding(ll_SCC, t_tmplink[1]))
                    lt_SCClinks.append(t_SCClink)
            elif l_remained_links[i][1] in i_lSCC[1]:
                t_tmplink = l_remained_links.pop(i)
                t_SCClink = (node_position_finding(ll_SCC, t_tmplink[0]), i_lSCC[0])
                lt_SCClinks.append(t_SCClink)

    lt_SCClinks = list(set(lt_SCClinks))

    return(lt_SCClinks)
    
    
def node_position_finding(llSCC, s_node):
    """
    sub function of 'net_of_SCCs'
    llSCC = [[node1,node2,node3... nodes in the SCC1],[node6,node7.... nodes in the SCC2],....]
    s_node is node name
    """
    for i_lSCC in enumerate(llSCC):
        if s_node in i_lSCC[1]:
            return(i_lSCC[0])
    else:
        print("error")
        return