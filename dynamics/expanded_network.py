# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 21:04:25 2019

@author: jwKim
"""

import numpy as np
import time

from .Boolean_functions import get_minimized_Boolean_logic_equation_using_Quine_McCluskey_algorithm_from_truthtable as get_min_Boolean_eq
from ..topology_analysis.feedback_analysis import find_all_feedbacks_Johnson
from ..topology_analysis.FVS_analysis import conversion_of_combination_num_to_list_of_comb
#from ..support_functions.combination_functions import calculate_next_combination
from ..support_functions import combination_functions
from . import dynamics_supporting_module

def make_expanded_network_using_Boolean_truthtable(networkmodel, networkmodel_expanded):
    for s_nodename in networkmodel.show_nodenames():
        if ' ' in s_nodename:
            raise ValueError("there is node name with space. to make expanded network, all node name has no space")
        networkmodel_expanded.add_node(s_nodename+networkmodel_expanded.show_suffix_on())
        networkmodel_expanded.add_node(s_nodename+networkmodel_expanded.show_suffix_off())
    
    for node_expanded in networkmodel_expanded.show_single_nodes():
        print(str(node_expanded)+"'s calculation starts")
        l_logic_equation = get_minimized_Boolean_function_node_using_QM(networkmodel, node_expanded)
        add_and_connect_upper_nodes_to_expanded_node(networkmodel, networkmodel_expanded, node_expanded, l_logic_equation)
    
    #delete duplicated andnode. 
    #for example, if 'a_0__AND__b_0' and 'b_0__AND__a_0' nodes exist together, delete one.
    for i, node_expanded in enumerate(networkmodel_expanded.show_composite_nodes()):
        set_coponents = set(node_expanded.show_list_of_elements_in_composite())
        for node_compared in networkmodel_expanded.show_composite_nodes()[i+1:]:
            set_components_compared = set(node_compared.show_list_of_elements_in_composite())
            if set_coponents == set_components_compared:
                ls_node_regulating = node_expanded.show_regulating_nodenames()
                for s_node in node_compared.show_regulating_nodenames():
                    if s_node not in ls_node_regulating:
                        networkmodel_expanded.add_directed_link(str(node_expanded), s_node)
                networkmodel_expanded.delete_node(str(node_compared))


def get_minimized_Boolean_function_node_using_QM(networkmodel, node_of_expandedmodel):
    """node_of_expandedmodel should be single node(not composite node)"""
    #print(str(node_of_expandedmodel))
    s_node_originalmodel = node_of_expandedmodel.show_original_name()
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
    if node_of_expandedmodel.is_on_state_node():
        l_logic_equation = get_min_Boolean_eq(i_Boolean_truthtable, l_orderd_name_regulators, True)
    else:
        i_Boolean_truthtable = (pow(2,pow(2,len(l_orderd_name_regulators))) -1) - i_Boolean_truthtable# not equation of Boolean logic
        l_logic_equation = get_min_Boolean_eq(i_Boolean_truthtable, l_orderd_name_regulators, True)

    #s_logic_equation is like '((NOT B) OR (NOT A))' or '((a AND b) OR c)' or  '(a AND b AND c)' ....
    #print(str(node_of_expandedmodel), l_logic_equation)
    return l_logic_equation

def add_and_connect_upper_nodes_to_expanded_node(networkmodel, networkmodel_expanded, node_of_expandedmodel, l_logic_equation):
    s_node_originalmodel = node_of_expandedmodel.show_original_name()
    node_of_originalmodel = networkmodel.select_node(s_node_originalmodel)
    if l_logic_equation == None:#when this node is source node
        return
    elif l_logic_equation == ['1']:
        l_nodes_regulator = node_of_originalmodel.show_regulator_nodes()
        ls_nodes_regulator = [str(node) for node in l_nodes_regulator]
        ls_nodes_regulator = list(set(ls_nodes_regulator))#delete duplication
        if str(node_of_originalmodel) in ls_nodes_regulator:#self loop
            networkmodel_expanded.add_directed_link(str(node_of_expandedmodel),str(node_of_expandedmodel))
            networkmodel_expanded.add_directed_link(node_of_expandedmodel.show_name_complementary(),str(node_of_expandedmodel))
            ls_nodes_regulator.pop(ls_nodes_regulator.index(str(node_of_originalmodel)))
        for s_node in ls_nodes_regulator:
            networkmodel_expanded.add_directed_link(s_node+networkmodel_expanded.show_suffix_on(), str(node_of_expandedmodel))
            networkmodel_expanded.add_directed_link(s_node+networkmodel_expanded.show_suffix_off(), str(node_of_expandedmodel))
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
                    s_logic_part = s_logic_part+networkmodel_expanded.show_suffix_on()#make all node to be on node. if NOT exist, change on node to off node
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
                    s_tmp = s_tmp[:-len(networkmodel_expanded.show_suffix_on())]
                    l_stack.append(s_tmp+networkmodel_expanded.show_suffix_off())
                elif ("AND" in l_temp) and not ("OR" in l_temp):
                    s_tmp = ''.join(l_temp)
                    s_tmp = s_tmp.replace("AND",networkmodel_expanded.show_andnode_connector())
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
            if networkmodel_expanded.show_andnode_connector() in s_node_new:
                for s_node_upper in s_node_new.split(networkmodel_expanded.show_andnode_connector()):
                    #print(s_node_new)
                    networkmodel_expanded.add_directed_link(s_node_upper, s_node_new)
                    #connect newly made andnodes to upper nodes

def find_stable_motifs_using_expanded_net(expanded_network):
    ls_nodenames = expanded_network.show_nodenames()
    lt_links = expanded_network.show_links_list_of_tuple()
    ll_stable_motif = []
    ll_feedbacks = find_all_feedbacks_Johnson(ls_nodenames, lt_links)
    print("the number of feedbacks in expanded network is ", len(ll_feedbacks))
    
    s_suffix_of_on_node = expanded_network.show_suffix_on()
    s_suffix_of_off_node = expanded_network.show_suffix_off() #if s_suffix_of_on_node[-len(s_suffix_of_off_node):] == s_suffix_of_off_node then occurs bug. vice versa
    s_andnode_connector = expanded_network.show_andnode_connector()
    
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
                i_combination = combination_functions.calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
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
                i_combination = combination_functions.calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
                continue
            
            if set_nodes_in_andnode_combination.issubset(set_candidate_of_stablemotif):
                ll_stable_motif_combinations.append(l_combination)
                lset_stable_motif_contatining_andnodes.append(set_candidate_of_stablemotif)
            
            i_combination = combination_functions.calculate_next_combination(i_combination, len(lset_feedbacks_filtered_l_andnodes))
        
    
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

def find_stable_motifs_using_prime_implicants(expanded_network, min_size=1, max_size=None):#similar principle to maximal trap space finding
    obj_prime_implicants = Prime_implicants(expanded_network)
    net_original = expanded_network.show_original_network()
    l_nodenames_original = net_original.show_nodenames()
    if max_size == None:
        max_size = len(net_original.show_nodenames())
    
    l_stable_motifs_known = []
    for i_size in range(min_size, max_size+1):
        print(i_size," size stable motifs are now calculating")
        f_start_time = time.time()
        for i_comb in combination_functions.generator_combination_num_in_defined_1(len(net_original.show_nodenames()), i_size):
            array_nodes_selected = np.nonzero(list(reversed([int(s) for s in bin(i_comb)[2:]])))[0]
            l_nodenames_subnet = [l_nodenames_original[i] for i in array_nodes_selected]
            net_sub = net_original.make_subnetwork(l_nodenames_subnet)
            dic_code_lSCC, lt_SCC_hierarchy = net_sub.show_SCC_decomposition()
            if len(dic_code_lSCC) >=2:
                #print(l_nodenames_subnet, "is not SCC")
                continue
            else:
                for i_state in range(pow(2,i_size)):
                    array_state = dynamics_supporting_module.int_to_arraystate(i_state, i_size)
                    array_state = (array_state*2)-1#1->1, 0->-1
                    array_state.dtype = int
                    array_state_full = np.zeros((len(l_nodenames_original),),dtype=int)
                    array_state_full[array_nodes_selected] = array_state
                    stable_motif_candidate = Stable_motif(array_state_full)
                    if stable_motif_candidate.check_containment_smalelr_SMs(l_stable_motifs_known):
                        continue
                    else:
                        if obj_prime_implicants.check_stable_motif(stable_motif_candidate):
                            l_stable_motifs_known.append(stable_motif_candidate)
        
        print(i_size," size stable motifs finding ended")
        print("it takes ",time.time()-f_start_time)
    
    return l_stable_motifs_known, l_nodenames_original
    
class Prime_implicants:
    def __init__(self, expanded_net):
        self.l_ordered_nodenames = expanded_net.show_original_nodenames()
        self.matrix_prime_implicants = None
        self.dict_node_array_position_of_prime_implicants = {}
        
        self.calculate_prime_implicants(expanded_net)
        
        #self.matrix_1or0 = self.matrix_prime_implicants * self.matrix_prime_implicants#componenetwise multiplication
        self.array_num_of_nonzero_in_prime_implicants = np.array([np.count_nonzero(row) for row in self.matrix_prime_implicants])
        
    
    def calculate_prime_implicants(self, expanded_network):
        i_counter = 0
        l_prime_implicants = []#elements are expanded node
        l_suffixs = [expanded_network.show_suffix_off(), expanded_network.show_suffix_on()]
        dict_name_value_array_positions = {}
        for i_index in range(len(self.l_ordered_nodenames)):
            #print(i_index)
            for i_value, s_suffix in enumerate(l_suffixs):
                #print(s_suffix)
                expanded_node = expanded_network.select_node(self.l_ordered_nodenames[i_index]+s_suffix)
                l_regulator_expanded_nodes = expanded_node.show_regulator_nodes()
                if not l_regulator_expanded_nodes:#maybe input node
                    l_regulator_expanded_nodes = [expanded_node]
                #print(l_regulator_expanded_nodes)
                l_prime_implicants.extend(l_regulator_expanded_nodes)
                dict_name_value_array_positions[(i_index, 2*i_value-1)] = (i_counter, i_counter + len(l_regulator_expanded_nodes))
                i_counter += len(l_regulator_expanded_nodes)
        
        self.matrix_prime_implicants = np.zeros((len(l_prime_implicants), len(self.l_ordered_nodenames)), dtype=int)
        #print(l_prime_implicants)
    
        for key in dict_name_value_array_positions.keys():
            t_position = dict_name_value_array_positions[key]
            array_positions = np.zeros((len(l_prime_implicants),), dtype=bool)
            array_positions[t_position[0]:t_position[1]] = 1
            array_positions.shape = (1,len(array_positions))
            self.dict_node_array_position_of_prime_implicants[key]= array_positions
        #print(self.dict_node_array_position_of_prime_implicants)
        
        for i, exp_node_prime_implicant in enumerate(l_prime_implicants):
            if exp_node_prime_implicant.is_composite_node():
                l_s_expandednode_component = exp_node_prime_implicant.show_list_of_elements_in_composite()
                for s_expandendnode in l_s_expandednode_component:
                    expanded_node = expanded_network.select_node(s_expandendnode)
                    i_position = self.l_ordered_nodenames.index(expanded_node.show_original_name())
                    if expanded_node.is_on_state_node():
                        self.matrix_prime_implicants[i][i_position] = 1
                    else:
                        self.matrix_prime_implicants[i][i_position] = -1
            else:#single node
                i_position = self.l_ordered_nodenames.index(exp_node_prime_implicant.show_original_name())
                if exp_node_prime_implicant.is_on_state_node():
                    self.matrix_prime_implicants[i][i_position] = 1
                else:
                    self.matrix_prime_implicants[i][i_position] = -1
        
        #print(self.matrix_prime_implicants)
    
    def check_stable_motif(self, stable_motif):
        array_state_SM = stable_motif.show_array_state()
        #print(array_state_SM)
        
        lt_node_state_of_SM = [(i_index, array_state_SM[i_index]) for i_index in np.nonzero(array_state_SM)[0]]
        #print(lt_node_state_of_SM)
        matrix_filter = np.concatenate([self.dict_node_array_position_of_prime_implicants[t_key] for t_key in lt_node_state_of_SM], axis=0)
        #print(matrix_filter)
        #print(np.matmul(self.matrix_prime_implicants, array_state_SM))
        #array_check_result = ((np.matmul(self.matrix_prime_implicants, array_state_SM) - np.matmul(self.matrix_1or0, array_1or0)) == 0)
        array_check_result = ((np.matmul(self.matrix_prime_implicants, array_state_SM) - self.array_num_of_nonzero_in_prime_implicants) == 0)
        #print(array_check_result)
        if (np.matmul(matrix_filter, array_check_result)).all():
            return True
        else:
            return False
        
        
class Stable_motif:
    def __init__(self, array_state):
        self.array_state = array_state # 1 means on, -1 means off, 0 means irrelevant to this stable motif
        self.array_state_1or0 = array_state*array_state
    
    def check_containment_smalelr_SMs(self, l_stable_motifs_known):
        for stable_motif in l_stable_motifs_known:
            if self.check_containment_smaller_SM(stable_motif):
                return True #this state is not stable motif(not minimal motif)
        return False
            
    def check_containment_smaller_SM(self, stable_motif_known):
        i_num_nodes = self.show_num_of_nodes_in_SM()
        i_num_nodes_known = stable_motif_known.show_num_of_nodes_in_SM()
        if i_num_nodes_known >= i_num_nodes:
            return False
        if np.dot(stable_motif_known.show_array_state(), self.array_state) == i_num_nodes_known:
            return True
        else: return False
            
    def show_array_state(self):
        return self.array_state
    
    def show_num_of_nodes_in_SM(self):
        return np.count_nonzero(self.array_state)
    
    def check_prime_implicants(self, dict_prime_implicants):
        for i_index in np.nonzero(self.array_state)[0]:
            t_index_state = (i_index, self.array[i_index])
            np.multiply(dict_prime_implicants[t_index_state], self.array_state)
    

