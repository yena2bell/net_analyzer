# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 19:31:21 2019

@author: jwKim
"""
import itertools
from collections import defaultdict
import numpy as np
from . import FVS_analysis, SCC_analysis, basic_topology_functions

def find_all_downstream_from_seed(lt_links, s_seed, ls_ends=[], b_downstream_ended_only_ls_ends=False):
    """this function find all possible downstream of s_seed.
    downstreams calculation ends when there is no link to connect or it reachs the element of ls_ends.
    ***caution!! lt_links should be acyclic or there is no feedback between s_seed and elements of ls_ends ***
    lt_links is the list of tuples which contain link information of the network.
    element of lt_links can have two form: (s_start_node1,s_end_node2) or(s_start_node1,'+',s_end_node2).
    two forms can be contained simultaneously."""
    llt_downstreams = []
    dic_s_start_l_links = {}
    for t_link in lt_links:
        dic_s_start_l_links.setdefault(t_link[0],[]).append(t_link)
        
    llt_stack = []
    for t_link in dic_s_start_l_links[s_seed]:
        llt_stack.append([t_link])
        
    while llt_stack:
        lt_downstream = llt_stack.pop()
        if lt_downstream[-1][-1] in ls_ends:
            llt_downstreams.append(lt_downstream)
            continue
        if lt_downstream[-1][-1] not in dic_s_start_l_links.keys():
            if b_downstream_ended_only_ls_ends:
                continue
            else:
                llt_downstreams.append(lt_downstream)
                continue
        for t_link in dic_s_start_l_links[lt_downstream[-1][-1]]:
            llt_stack.append(lt_downstream+[t_link])
    
    return llt_downstreams


def get_all_cycles(l_values):
    """gel all cycles (similar to permutation) from the l_values
    return list of cycles which is tuple form.
    for example, if l_value is ['a','b','c'] then return
    [('a'),('b'),('c'),('a','b'),('a','c'),('b','c'),('a','b','c'),('a','c','b')]"""
    lt_cycles = []
    i_num = len(l_values)
    for i in range(i_num):
        for j in range(i_num):
            for t_permutation in itertools.permutations(l_values[j:],i+1):
                if t_permutation[0] == l_values[j]:
                    lt_cycles.append(t_permutation)
        
    return lt_cycles

            
def find_all_feedback_from_FVS(lt_links, ls_FVS=None):
    """find all feedbacks.
    for safty, let the network made by lt_links be SCC.
    element of lt_links can be form of (start node, end node) or (start node, modality('+' or '-'), end node)
    this code use FVS. if FVS are already gained, putting them in ls_FVS variable save the time."""
    if not ls_FVS:
        set_nodes = set([])
        for t_link in lt_links:
            set_nodes.add(t_link[0])
            set_nodes.add(t_link[1])
        ls_FVS = FVS_analysis.FVS_finding(list(set_nodes), lt_links)[0]
    #if FVS nodes are already gained, pass this step
    
    llt_feedbacks = []
    dic_ts_FVSnodepair_llt_downstreams = {}#{(FVS node1, FVS node2):list of lt_downstream which starts at FVS node1 and ends at FVS node2}
    for s_FVSnode in ls_FVS:
        llt_downstreams = find_all_downstream_from_seed(lt_links, s_FVSnode, ls_FVS)
        for lt_downstream in llt_downstreams:
            ts_FVSpair = (s_FVSnode, lt_downstream[-1][-1])
            dic_ts_FVSnodepair_llt_downstreams.setdefault(ts_FVSpair,[]).append(lt_downstream)
    
    lts_cyclesofFVS = get_all_cycles(ls_FVS)
    for ts_cycleofFVS in lts_cyclesofFVS:
        if len(ts_cycleofFVS) == 1:
            llt_feedbacks.extend(dic_ts_FVSnodepair_llt_downstreams[(ts_cycleofFVS[0],ts_cycleofFVS[0])])
        else:
            b_stopflag = False
            lllt_feedbackfragment = []
            for i in range(len(ts_cycleofFVS)-1):
                lllt_feedbackfragment.append(dic_ts_FVSnodepair_llt_downstreams[(ts_cycleofFVS[i], ts_cycleofFVS[i+1])])
                if not dic_ts_FVSnodepair_llt_downstreams[(ts_cycleofFVS[i], ts_cycleofFVS[i+1])]:
                    b_stopflag = True
                    break
            lllt_feedbackfragment.append(dic_ts_FVSnodepair_llt_downstreams[(ts_cycleofFVS[-1],ts_cycleofFVS[0])])
            if not dic_ts_FVSnodepair_llt_downstreams[(ts_cycleofFVS[-1],ts_cycleofFVS[0])]:
                b_stopflag = True
            if b_stopflag:
                continue#if there is no feedback passing by all FVS nodes of that cycle, pass to next cycle
        
            llt_feedbacks_specific_cycle = lllt_feedbackfragment.pop(0)
            while lllt_feedbackfragment:
                llt_fragments_next = lllt_feedbackfragment.pop(0)
                llt_feedbacks_updated = []
                for lt_fragment in llt_feedbacks_specific_cycle:
                    for lt_fragment_next in llt_fragments_next:
                        ls_route = [t_link[1] for t_link in lt_fragment[:-1]]
                        ls_route_next = [t_link[1] for t_link in lt_fragment_next[:-1]]
                        if not set(ls_route).intersection(set(ls_route_next)):
                            llt_feedbacks_updated.append(lt_fragment+lt_fragment_next)
                llt_feedbacks_specific_cycle = llt_feedbacks_updated
            llt_feedbacks.extend(llt_feedbacks_specific_cycle)

    return llt_feedbacks


def find_all_feedbacks_Tarjan(ls_nodenames, lt_links):
    """lt_links have element of (startnodename, endnodename)
    use tarjan algorithm in each decomposed SCC"""
    
    ll_SCC = SCC_analysis.decompose_SCC(ls_nodenames, lt_links)
    ll_feedbacks = []
    for l_SCC in ll_SCC:
        lt_links_in_SCC = basic_topology_functions.extract_subnet_topology(lt_links, l_SCC)
        print("feedbacks are calculated in subnetwork with ",len(l_SCC)," nodes")
        
        dic_startnode_endnodes = {}
        for s_nodename in l_SCC:
            dic_startnode_endnodes[s_nodename] = []
            for t_link in lt_links_in_SCC:
                if t_link[0] == s_nodename:
                    dic_startnode_endnodes[s_nodename].append(t_link[-1])
                    #print(dic_startnode_endnodes)
        dic_node_counter = {}
        for s_nodename in l_SCC:
            dic_node_counter[s_nodename] = len(dic_startnode_endnodes[s_nodename])-1
        #print(dic_node_counter)
        for s_node_trajectorystart in dic_node_counter.keys():
            if dic_node_counter[s_node_trajectorystart] == -1: #this means that all feedback containing this node are all calculated
                continue
            else:
                l_trajectory = [s_node_trajectorystart]
                while l_trajectory:
                    #print(l_trajectory)
                    i_counter = dic_node_counter[l_trajectory[-1]]
                    if i_counter == -1:
                        dic_node_counter[l_trajectory[-1]] = len(dic_startnode_endnodes[l_trajectory[-1]])-1
                        l_trajectory.pop()
                        if l_trajectory:
                            dic_node_counter[l_trajectory[-1]] -= 1
                    else:
                        s_node_next = dic_startnode_endnodes[l_trajectory[-1]][i_counter]
                        if s_node_next == s_node_trajectorystart:
                            ll_feedbacks.append(list(l_trajectory))
                            if len(ll_feedbacks)%20000 == 0:
                                print("calculated feedbacks are now ",len(ll_feedbacks))
                            
                        if s_node_next in l_trajectory:
                            dic_node_counter[l_trajectory[-1]] -= 1
                        else:
                            l_trajectory.append(s_node_next)
                dic_startnode_endnodes[s_node_trajectorystart] = []
                dic_node_counter[s_node_trajectorystart] =-1
    
    return ll_feedbacks

def find_all_feedbacks_Johnson(ls_nodenames, lt_links):
    ll_SCC = SCC_analysis.decompose_SCC(ls_nodenames, lt_links)
    lli_feedbacks = []
    ll_feedbacks = []
    
    def _unblock(i, 
                 dic_blocked_link, 
                 array_blocked):        
        if array_blocked[i]:#i is blocked:
            array_blocked[i] = False
        if dic_blocked_link[i]:
            for j in list(dic_blocked_link[i]):
                dic_blocked_link[i].discard(j)
                _unblock(j, dic_blocked_link, array_blocked)
    
    for l_SCC in ll_SCC:
        for i in range(len(l_SCC)):
            ls_nodes_refined = l_SCC.copy()[i:]
            lt_links_refined = basic_topology_functions.extract_subnet_topology(lt_links, ls_nodes_refined)
            if i >= 1:
                ll_SCC_in_SCC =  SCC_analysis.decompose_SCC(ls_nodes_refined, lt_links_refined)
                for l_SCC_in_SCC in ll_SCC_in_SCC:
                    if l_SCC[i] in l_SCC_in_SCC:
                        ls_nodes_refined = l_SCC_in_SCC
                        ls_nodes_refined = [l_SCC[i]] + ls_nodes_refined[:ls_nodes_refined.index(l_SCC[i])]+ls_nodes_refined[ls_nodes_refined.index(l_SCC[i])+1:]
                        lt_links_refined = basic_topology_functions.extract_subnet_topology(lt_links_refined, ls_nodes_refined)
                        break
            #get SCC from nodes of l_SCC[i:] which contains l_SCC[i]
            if len(ls_nodes_refined) == 1:
                if lt_links_refined: #SCC with one node and self loop
                    ll_feedbacks.append([ls_nodes_refined[0]])
                continue
            
            dic_istart_liends = defaultdict(list)
            for t_link in lt_links_refined:
                i_start= ls_nodes_refined.index(t_link[0])
                i_end = ls_nodes_refined.index(t_link[-1])
                dic_istart_liends[i_start].append(i_end)
            for i_key, li_ends in dic_istart_liends.items():
                dic_istart_liends[i_key] = list(set(li_ends))
            dic_istart_icount = {i_key:len(l_links)-1 for i_key,l_links in dic_istart_liends.items()}
            
            array_blocked = np.zeros_like(ls_nodes_refined, dtype=bool)
            dic_blocked_link = defaultdict(set)#if dic_blocked_link[i] contains j, then j->i link is blocked
            l_flow = []
            l_connectable_to_0 = []#has same length to l_flow. if l_connectable_to_0[i] = True: l_flow[:i+1] can reach to 0(root node)
            
            i_node = 0
            l_flow.append(i_node)
            l_connectable_to_0.append(False)
            array_blocked[i_node] = True
            while l_flow:
                i_next_edge = dic_istart_icount[i_node]
                if i_next_edge >= 0:
                    j_node = dic_istart_liends[i_node][i_next_edge]
                    dic_istart_icount[i_node] -= 1
                    if j_node == 0:
                        l_connectable_to_0[-1] = True
                        lli_feedbacks.append(l_flow.copy())
                    elif not array_blocked[j_node]:
                        i_node = j_node
                        l_flow.append(i_node)
                        l_connectable_to_0.append(False)
                        array_blocked[i_node] = True
                else:
                    i_end = l_flow.pop(-1)
                    b_end = l_connectable_to_0.pop(-1)
                    if l_flow:
                        dic_istart_icount[i_end] = len(dic_istart_liends[i_end])-1
                        if b_end:
                            _unblock(i_end, dic_blocked_link, array_blocked)
                            l_connectable_to_0[-1] = True
                        else:
                            for j in dic_istart_liends[i_end]:
                                dic_blocked_link[j].add(i_end)
                        i_node = l_flow[-1]
            
            while lli_feedbacks:
                li_feedback = lli_feedbacks.pop()
                ll_feedbacks.append([ls_nodes_refined[i] for i in li_feedback])
    

        
    return ll_feedbacks

    