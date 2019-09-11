# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 21:04:25 2019

@author: jwKim
"""



from .Boolean_functions import get_minimized_Boolean_logic_equation_using_Quine_McCluskey_algorithm_from_truthtable as get_min_Boolean_eq
from ..network import network
from ..topology_analysis.feedback_analysis import find_all_feedback
from ..topology_analysis.FVS_analysis import conversion_of_combination_num_to_list_of_comb
from ..support_functions.combination_functions import calculate_next_combination

s_suffix_of_on_node = "_1"
s_suffix_of_off_node = "_0" #if s_suffix_of_on_node[-len(s_suffix_of_off_node):] == s_suffix_of_off_node then occurs bug. vice versa
s_andnode_connector = "__AND__"

def make_expanded_network_using_Boolean_truthtable(networkmodel):
    networkmodel_expanded = network.Expanded_network("expanded_network_of_"+str(networkmodel))
    for s_nodename in networkmodel.show_nodenames():
        if ' ' in s_nodename:
            raise ValueError("there is node name with space. to make expanded network, all node name has no space")
        networkmodel_expanded.add_node(s_nodename+s_suffix_of_on_node)
        networkmodel_expanded.add_node(s_nodename+s_suffix_of_off_node)
    
    l_node_expanded_except_andnode = list(networkmodel_expanded.show_node())
    for node_expanded in l_node_expanded_except_andnode:
        print(str(node_expanded)+"'s calculation starts")
        l_logic_equation = get_minimized_Boolean_function_node_using_QM(networkmodel, node_expanded)
        #print(l_logic_equation)
        add_and_connect_upper_nodes_to_expanded_node(networkmodel, networkmodel_expanded, node_expanded, l_logic_equation)
    
    #delete duplicated andnode. 
    #for example, if 'a_0__AND__b_0' and 'b_0__AND__a_0' nodes exist together, delete one.
    for i, node_expanded in enumerate(networkmodel_expanded.show_node()):
        if s_andnode_connector in str(node_expanded):
            set_coponents = set(str(node_expanded).split(s_andnode_connector))
            for node_compared in networkmodel_expanded.show_node()[i+1:]:
                if s_andnode_connector in str(node_compared):
                    set_components_compared = set(str(node_compared).split(s_andnode_connector)) 
                    if set_coponents == set_components_compared:
                        networkmodel_expanded.delete_node(str(node_compared))
                else:
                    continue
        else:
            continue
            
    return networkmodel_expanded

def get_minimized_Boolean_function_node_using_QM(networkmodel, node_of_expandedmodel):
    #print(str(node_of_expandedmodel))
    s_node_originalmodel = str(node_of_expandedmodel)[:-len(s_suffix_of_on_node)] if str(node_of_expandedmodel)[-len(s_suffix_of_on_node):] == s_suffix_of_on_node else str(node_of_expandedmodel)[:-len(s_suffix_of_off_node)]
    #print(s_node_originalmodel)
    node_of_originalmodel = networkmodel.select_node(s_node_originalmodel)
    l_orderd_name_regulators = node_of_originalmodel.show_orderedname_regulators_truthtable()
    i_Boolean_truthtable = node_of_originalmodel.show_integerform_of_Boolean_truthtable()
    # regulator order of QM is reversed to my Boolean truthtable
    # for my truthtable, ('a','b','c') == (1,1,0) -> this regulator state is in 3(=1*1+1*2+0*4)+1 th row of truth table
    # but in QM, ('a','b','c') == (1,1,0) regulator state is 6(= 1*4+1*2+0*1) +1 th row.
    #so be careful in this part
    
    if not l_orderd_name_regulators:#when this node is source node
        return None
    
    if str(node_of_expandedmodel)[-len(s_suffix_of_on_node):] == s_suffix_of_on_node:
        l_logic_equation = get_min_Boolean_eq(i_Boolean_truthtable, l_orderd_name_regulators, True)
    elif str(node_of_expandedmodel)[-len(s_suffix_of_off_node):] == s_suffix_of_off_node:
        i_Boolean_truthtable = (pow(2,pow(2,len(l_orderd_name_regulators))) -1) - i_Boolean_truthtable# not equation of Boolean logic
        l_logic_equation = get_min_Boolean_eq(i_Boolean_truthtable, l_orderd_name_regulators, True)
    else:
        raise ValueError("incorrect suffix to the expanded network node!")

    #s_logic_equation is like '((NOT B) OR (NOT A))' or '((a AND b) OR c)' or  '(a AND b AND c)' ....
    #print(str(node_of_expandedmodel), l_logic_equation)
    return l_logic_equation

def add_and_connect_upper_nodes_to_expanded_node(networkmodel, networkmodel_expanded, node_of_expandedmodel, l_logic_equation):
    s_node_originalmodel = str(node_of_expandedmodel)[:-len(s_suffix_of_on_node)] if str(node_of_expandedmodel)[-len(s_suffix_of_on_node):] == s_suffix_of_on_node else str(node_of_expandedmodel)[:-len(s_suffix_of_off_node)]
    node_of_originalmodel = networkmodel.select_node(s_node_originalmodel)
    if l_logic_equation == None:#when this node is source node
        return
    elif l_logic_equation == ['1']:
        l_nodes_regulator = node_of_originalmodel.show_regulator_nodes()
        ls_nodes_regulator = [str(node) for node in l_nodes_regulator]
        ls_nodes_regulator = list(set(ls_nodes_regulator))#delete duplication
        if str(node_of_originalmodel) in ls_nodes_regulator:#self loop
            networkmodel_expanded.add_directed_link(str(node_of_expandedmodel),str(node_of_expandedmodel))
            ls_nodes_regulator.pop(ls_nodes_regulator.index(str(node_of_originalmodel)))
        for s_node in ls_nodes_regulator:
            networkmodel_expanded.add_directed_link(s_node+s_suffix_of_on_node, str(node_of_expandedmodel))
            networkmodel_expanded.add_directed_link(s_node+s_suffix_of_off_node, str(node_of_expandedmodel))
    elif l_logic_equation == ['0']:
        pass#no upper node. any expanded node can turn on this node.
    else:
        #maybe this minimized equation is composed of and combined terms combined by or. 
        #((A and B and (not C)) or (E and D))
        l_stack = []
        while l_logic_equation:
            s_logic_part = l_logic_equation.pop(0)
            if not (s_logic_part == ')'):
                if s_logic_part not in ['(',"NOT","AND","OR"]:
                    s_logic_part = s_logic_part+s_suffix_of_on_node#make all node to be on node. if NOT exist, change on node to off node
                l_stack.append(s_logic_part)
            else:
                l_temp = []
                s_logic_part = l_stack.pop()
                while s_logic_part != '(':
                    l_temp.append(s_logic_part)
                    s_logic_part = l_stack.pop()
                l_temp.reverse()
                if (l_temp[0] == "NOT") and (len(l_temp) == 2):
                    s_tmp = l_temp[1]
                    s_tmp = s_tmp[:-len(s_suffix_of_on_node)]
                    l_stack.append(s_tmp+s_suffix_of_off_node)
                elif ("AND" in l_temp) and not ("OR" in l_temp):
                    s_tmp = ''.join(l_temp)
                    s_tmp = s_tmp.replace("AND",s_andnode_connector)
                    l_stack.append(s_tmp)
                elif ("OR" in l_temp) and not ("AND" in l_temp):
                    while l_temp:
                        s_tmp = l_temp.pop()
                        if s_tmp != "OR":
                            l_stack.append(s_tmp)
                else:
                    raise ValueError(str(node_of_expandedmodel)+" has not appropriate minimized logic equation")
                    
        for s_node_new in l_stack:
            networkmodel_expanded.add_node(s_node_new)
            networkmodel_expanded.add_directed_link(s_node_new, str(node_of_expandedmodel))
            if s_andnode_connector in s_node_new:
                for s_node_upper in s_node_new.split(s_andnode_connector):
                    #print(s_node_new)
                    networkmodel_expanded.add_directed_link(s_node_upper, s_node_new)
                    #connect newly made andnodes to upper nodes

def find_stable_motifs_using_expanded_net(ls_nodenames, lt_links):
    ll_stable_motif = []
    ll_feedbacks = find_all_feedback(ls_nodenames, lt_links)
    print("the number of feedbacks in expanded network is ", len(ll_feedbacks))
    
    def check_contradict_state_of_same_node_in_feedback(l_feedback):
        """if node_up, node_down co-exist in the l_feedback, return False
        else return True
        ignore andnodes."""
        ll_snode_1or0 = []
        for s_node_expanded in l_feedback:
            if s_andnode_connector not in s_node_expanded:
                if s_node_expanded[-len(s_suffix_of_on_node):] == s_suffix_of_on_node:
                    l_tmp = [s_node_expanded[:-len(s_suffix_of_on_node)],1]#[original_node_name,1] means original_node_name_on
                    if [s_node_expanded[:-len(s_suffix_of_on_node)],0] in ll_snode_1or0:
                        return False
                    else:
                        ll_snode_1or0.append(l_tmp)
                elif s_node_expanded[-len(s_suffix_of_off_node):] == s_suffix_of_off_node:
                    l_tmp = [s_node_expanded[:-len(s_suffix_of_on_node)],0]
                    if [s_node_expanded[:-len(s_suffix_of_on_node)],1] in ll_snode_1or0:
                        return False
                    else:
                        ll_snode_1or0.append(l_tmp)
        
        return True
    
    def find_andnode_from_feedback(l_feedback):
        """find all andnodes and return list of andnode"""
        ls_andnodes = []
        for s_node_expanded in l_feedback:
            if s_andnode_connector in s_node_expanded:
                ls_andnodes.append(s_node_expanded)
        return ls_andnodes
    
    lset_feedbacks_filtered_l_andnodes = []#list of l_feedback containing andnode and no contradicting node coexistness
    for l_feedback in ll_feedbacks:
        ls_andnodes = find_andnode_from_feedback(l_feedback)
        if ls_andnodes:
            l_feedback_tmp = l_feedback.copy()
            for s_andnode in ls_andnodes:
                l_feedback_tmp += s_andnode.split(s_andnode_connector)
            if check_contradict_state_of_same_node_in_feedback(l_feedback_tmp):
                lset_feedbacks_filtered_l_andnodes.append([set(l_feedback), ls_andnodes])
        else:#no andnode in the feedback
            if check_contradict_state_of_same_node_in_feedback(l_feedback):
                ll_stable_motif.append(l_feedback)
    print("the number of feedbacks containing andnodes and no contradicting nodes is ",len(lset_feedbacks_filtered_l_andnodes))
    
    #check all combination of ll_feedbacks_filtered_l_andnodes
    i_combination = 1
    ll_stable_motif_combinations = []
    lset_stable_motif_contatining_andnodes= []
    while i_combination:
        l_combination = conversion_of_combination_num_to_list_of_comb(i_combination,0)
        for l_combination_stablemotif in ll_stable_motif_combinations:
            if l_combination_stablemotif in l_combination:
                i_combination = calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
                break
            #if new combination already contains stable motif found, through that combination
        else:  
            set_candidate_of_stablemotif = set([])
            l_andnodes_of_combination = []
            
            for i_position in l_combination:
                set_candidate_of_stablemotif = set_candidate_of_stablemotif.union(lset_feedbacks_filtered_l_andnodes[i_position][0])
                l_andnodes_of_combination += lset_feedbacks_filtered_l_andnodes[i_position][1]
            
            set_nodes_in_andnode_combination = set([])
            for s_andnode in l_andnodes_of_combination:
                for s_node in s_andnode.split(s_andnode_connector):
                    set_nodes_in_andnode_combination.add(s_node)
            
            if not check_contradict_state_of_same_node_in_feedback(list(set_nodes_in_andnode_combination.union(set_candidate_of_stablemotif))):
                i_combination = calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
                continue
            
            if set_nodes_in_andnode_combination.issubset(set_candidate_of_stablemotif):
                ll_stable_motif_combinations.append(l_combination)
                lset_stable_motif_contatining_andnodes.append(set_candidate_of_stablemotif)
            
            i_combination = calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
        
    
    #check whether stable module containing and node is superset of stable motif without andnode
    ll_stable_motif_containing_andnode=[]
    for set_stable_motif_containing_andnodes in lset_stable_motif_contatining_andnodes:
        for l_stable_motif_no_andnode in ll_stable_motif:
            if set_stable_motif_containing_andnodes.issuperset(l_stable_motif_no_andnode):
                break
        else:
            ll_stable_motif_containing_andnode.append(list(set_stable_motif_containing_andnodes))
    
    #delete duplications
    for i, l_motif_containing_andnode in enumerate(ll_stable_motif_containing_andnode):
        for j in range(len(ll_stable_motif_containing_andnode)-1,i,-1):
            if set(l_motif_containing_andnode) == set(ll_stable_motif_containing_andnode[j]):
                ll_stable_motif_containing_andnode.pop(j)
        
    return ll_stable_motif+ll_stable_motif_containing_andnode
        
    

