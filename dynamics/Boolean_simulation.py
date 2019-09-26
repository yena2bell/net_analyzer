# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 19:06:56 2019

@author: jwKim
"""
import numpy as np

from . import dynamics_supporting_module as DSM
from . import Boolean_functions

def extract_dynamics_information_from_network(network):#checked
    """state order is [input nodes] + [not input nodes]
    order of input nodes is determined by network.show_input_nodes()
    order of not input nodes is determined by network.show_not_input_nodes()
    it returns 4 variables.
    ls_inputnodenames, ls_not_inputnodenames are list of node names in order.
    order of all nodes is ls_inputnodenames+ls_not_inputnodenames
    dic_nodename_i_truthtable has (not input) node nams as a key and integer form truthtable as value
    dic_nodename_array_regulatorinfo has the same key to the dic_nodename_i_truthtable
    its value is an matrix. when this matrix is multiplied by overall state, it will returns array of state of regulators of that node
    i.e. array_state @ regulator_info_matrix_form = array_state_of_regulators
    
    if node is source node, i.e. node.show_integerform_of_Boolean_truthtable() == None,
    dic_nodename_i_truthtable and dic_nodename_array_regulatorinfo don't have that node as a key
    it means no touch that node when update the state
    """
    
    l_inputnodes = network.show_input_nodes()
    ls_inputnodenames = [str(node) for node in l_inputnodes]
    l_not_inputnodes = network.show_not_input_nodes()
    ls_not_inputnodenames = [str(node) for node in l_not_inputnodes]
    
    ls_nodename_ordered = ls_inputnodenames+ls_not_inputnodenames
    dic_nodename_array_regulatorinfo = {}
    dic_nodename_i_truthtable = {}
    for node in l_not_inputnodes:
        i_truthtable = node.show_integerform_of_Boolean_truthtable()
        if i_truthtable:#i_truthtable!=None.
            dic_nodename_i_truthtable[str(node)] = node.show_integerform_of_Boolean_truthtable()
            ls_regulators_ordered = node.show_orderedname_regulators_truthtable()
            li_regulators_ordered = [ls_nodename_ordered.index(nodename) for nodename in ls_regulators_ordered]
            array_tmp = np.array([[0]*len(li_regulators_ordered)]*len(ls_nodename_ordered))
            for i_column, i_row in enumerate(li_regulators_ordered):
                array_tmp[i_row][i_column] = 1
            dic_nodename_array_regulatorinfo[str(node)] = array_tmp
    
    return ls_nodename_ordered, ls_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo
    
        
def basin_calculation_for_specific_perturbation(l_order_nodes,
                                                ls_inputnodenames, 
                                                dic_nodename_i_truthtable, 
                                                dic_nodename_array_regulatorinfo, 
                                                lt_s_nodename_i_perturbedstate):
    """use Boolean synchronous update
    lt_s_nodename_i_perturbedstate = [(nodename, 1 or 0), (nodename, True of False),,,]
    if b_combine_output_in_one_file == True, outputs for each input_condition will be written in one file."""
    
    
    #check the lt_s_nodename_i_perturbedstate. and convert it to dic_snode_perturbed
    dic_snode_perturbed = dict(lt_s_nodename_i_perturbedstate)#key is perturbed node, value is perturbed state
    if len(dic_snode_perturbed) != len(lt_s_nodename_i_perturbedstate):
        raise ValueError("there are duplication in perturbation argument")
    for s_inputnode in ls_inputnodenames:
        if s_inputnode in dic_snode_perturbed.keys():
            raise ValueError(s_inputnode+" is input node but perturbed")
    
    #calculate basins for each input condition. and summarize basin information as integer_form_set.
    dic_i_inputcondition_l_basin = {}
    if ls_inputnodenames:
        for i_inputcondition in range(pow(2,len(ls_inputnodenames))):
            array_inputcondition = DSM.int_to_arraystate(i_inputcondition, len(ls_inputnodenames))
            print(i_inputcondition, " input condition calculation starts")
            l_basin = attractor_basin_calculation_for_specific_inputcondition_perturbation(l_order_nodes,
                                                                                           ls_inputnodenames,
                                                                                           array_inputcondition,
                                                                                           dic_snode_perturbed,
                                                                                           dic_nodename_i_truthtable,
                                                                                           dic_nodename_array_regulatorinfo)
            dic_i_inputcondition_l_basin[i_inputcondition] = l_basin
    
    else:#no input nodes
        array_inputcondition = np.array([])
        print("calculation start")
        l_basin = attractor_basin_calculation_for_specific_inputcondition_perturbation(l_order_nodes,
                                                                                       ls_inputnodenames,
                                                                                       array_inputcondition,
                                                                                       dic_snode_perturbed, 
                                                                                       dic_nodename_i_truthtable, 
                                                                                       dic_nodename_array_regulatorinfo)
                                                                       
        dic_i_inputcondition_l_basin[-1] = l_basin
    
    #input condition == -1 means no input nodes.
    #attractor calculation for each basin
    return dic_i_inputcondition_l_basin
        

def attractor_basin_calculation_for_specific_inputcondition_perturbation(l_order_nodes,
                                                                         ls_inputnodenames,
                                                                         array_input_state,
                                                                         dic_perturbed_state,
                                                                         dic_nodename_i_truthtable,
                                                                         dic_nodename_array_regulatorinfo):
    
    dic_i_index_i_truthtable = {l_order_nodes.index(s_nodename):dic_nodename_i_truthtable[s_nodename] for s_nodename in dic_nodename_i_truthtable.keys()}
    dic_i_index_array_regulatorinfo = {l_order_nodes.index(s_nodename):dic_nodename_array_regulatorinfo[s_nodename] for s_nodename in dic_nodename_i_truthtable.keys()}
    #conversion of {nodename:i_truthtable} to {index of node:i_truthtable}
    for s_perturbend_node in dic_perturbed_state.keys():
        i_index_perturbed = l_order_nodes.index(s_perturbend_node)
        if dic_perturbed_state[s_perturbend_node]:#perturbed to 0 or False
            dic_i_index_i_truthtable[i_index_perturbed] = 0
        else: #perturbed to 1 or True
            dic_i_index_i_truthtable[i_index_perturbed] = 1
        dic_i_index_array_regulatorinfo[i_index_perturbed] = np.array([[0]*0]*(len(l_order_nodes)))
        #dic_i_index_array_regulatorinfo[i_index_perturbed] will be matrix multiplied to all states. result will always be 0 value.
    #perturbation information is used to make dic_i_index_i_truthtable and dic_i_index_array_regulatorinfo
    #perturbation is applied in next_state_calculatrion function throuth dic_i_index_i_truthtable and dic_i_index_array_regulatorinfo
    dic_input_state = dict(zip(ls_inputnodenames, array_input_state))
    
    array_perturbed_state_input_state =  _array_perturbed_state_input_state(l_order_nodes, 
                                                                            dic_input_state, 
                                                                            dic_perturbed_state)
    matrix_converter = _matrix_converter_from_changable_to_all_state(l_order_nodes, 
                                                                     dic_input_state, 
                                                                     dic_perturbed_state)
    array_converter_state_to_int = _get_array_converter_state_to_int(l_order_nodes, 
                                                                     dic_input_state, 
                                                                     dic_perturbed_state)
    
    ifs_all = DSM.Integer_form_numberset(0)#set of all states calculated.
    l_basin = []
    for i in range(pow(2,len(l_order_nodes)-len(ls_inputnodenames)-len(dic_perturbed_state))):
        if ifs_all.has_the_number(i):#check whether this state is already calculated.
            continue
        else:
            i_next = i
            l_trajectory = []
            array_all = np.matmul(DSM.int_to_arraystate(i_next, len(matrix_converter)),matrix_converter)+array_perturbed_state_input_state
            while not ifs_all.has_the_number(i_next):
                ifs_all += i_next
                l_trajectory.append(i_next)
                array_next = next_state_calculatrion(array_all, dic_i_index_i_truthtable, dic_i_index_array_regulatorinfo)
                i_next = np.dot(array_next,array_converter_state_to_int)
                array_all = array_next
            for basin in l_basin:
                if basin.has_the_state_integer_form(i_next):
                    for i_state in l_trajectory:
                        basin.add_state_integer_form(i_state)
                    break
            else:
                basin_new = Basin_states()
                basin_new.set_input_states(dict(zip(ls_inputnodenames, array_input_state)))
                basin_new.set_perturbednode_states(dic_perturbed_state)
                basin_new.set_order_of_nodes(l_order_nodes)
                l_i_attractor = l_trajectory[l_trajectory.index(i_next):]
                basin_new.add_attractor_integer_form(l_i_attractor)
                for i_state in l_trajectory:
                    basin_new.add_state_integer_form(i_state)
                l_basin.append(basin_new)
                
    return l_basin
            

def next_state_calculatrion(array_state_all, dic_i_nodeindex_i_truthtable, dic_i_nodeindex_array_regulatorinfo):
    """array_state_all = concatenateion  of array_input_state and array_not_input_state
    perturbation effect is in dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo"""
    array_next = array_state_all.copy()
    
    for i_index in dic_i_nodeindex_i_truthtable.keys():
        array_state_regulator = np.matmul(array_state_all, dic_i_nodeindex_array_regulatorinfo[i_index])
        array_next[i_index] = Boolean_functions.Boolean_function(dic_i_nodeindex_i_truthtable[i_index], array_state_regulator)
    
    return array_next

            
def _get_array_converter_state_to_int(l_order_nodenames, dic_input_state, dic_perturbed_state):

    i_num_changing_nodes = len(l_order_nodenames)-len(dic_input_state)-len(dic_perturbed_state)
    l_tmp = list(range(i_num_changing_nodes))
    l_tmp = [pow(2,i) for i in l_tmp]
    l_tmp.reverse()
    l_index_inputs = []
    for s_node in dic_input_state.keys():
        l_index_inputs.append(l_order_nodenames.index(s_node))
    l_index_perturbed = []
    for s_node in dic_perturbed_state.keys():
        l_index_perturbed.append(l_order_nodenames.index(s_node))
    l_index_no_change = l_index_inputs+l_index_perturbed
    if len(l_index_no_change) != (len(l_index_inputs)+len(l_index_perturbed)):
        print("some input nodes are perturbed!")
        print("input node list is ",list(dic_input_state.keys()))
        print("perturbed node list is ",list(dic_perturbed_state.keys()))
    l_index_no_change.sort(reverse=True)
    for i in l_index_no_change:
        l_tmp.insert(i, 0)
    return np.array(l_tmp, dtype=int)
            

def _matrix_converter_from_changable_to_all_state(l_order_nodenames, dic_input_state, dic_perturbed_state):
    """when ls_not_inputnodenames = [a,b,c,d,e,f], and dic_s_nodename_i_perturbedstate = {b:0, e:1}
    array_perturbed_state = array([0,0,0,0,1,0])
    matrix_converter is 4*6 matrix. 
    if (a,c,e,f) = (1,0,1,0), then (1,0,1,0 ) @ matrix_converter + array_perturbed_state = (1,0,0,1,1,0)
    it can be used to make overall state from not perturbed nodes state"""
    
    i_num_changing_nodes = len(l_order_nodenames)-len(dic_input_state)-len(dic_perturbed_state)
    l_index_inputs = []
    for s_node in dic_input_state.keys():
        l_index_inputs.append(l_order_nodenames.index(s_node))
    l_index_perturbed = []
    for s_node in dic_perturbed_state.keys():
        l_index_perturbed.append(l_order_nodenames.index(s_node))
    l_index_no_change = l_index_inputs+l_index_perturbed
    
    matrix_converter = np.array([[0]*len(l_order_nodenames)]*i_num_changing_nodes, dtype=int)
    i_row = 0
    for i_column in range(len(l_order_nodenames)):
        if i_column not in l_index_no_change:
            matrix_converter[i_row][i_column] = 1
            i_row += 1
    return matrix_converter

def _array_perturbed_state_input_state(l_order_nodenames, dic_input_state, dic_perturbed_state):
    l_tmp = [0]*len(l_order_nodenames)
    for s_input in dic_input_state.keys():
        l_tmp[l_order_nodenames.index(s_input)] = dic_input_state[s_input]
    for s_perturbed in dic_perturbed_state.keys():
        l_tmp[l_order_nodenames.index(s_perturbed)] = dic_perturbed_state[s_perturbed]

    return np.array(l_tmp, dtype=int)
    

class Basin_states:
    def __init__(self):
        self.ifs_states = DSM.Integer_form_numberset(0)
        self.dic_input_state = {}
        self.l_order_nodes = []
        self.dic_perturbednode_state = {}
        self.array_converter_state_to_integer = None
        self.matrix_converter_chagable_to_all = None
        self.array_not_changed_state = None
        self.i_num_changing_nodes = None
        self.l_i_attractor = []
        self.i_num_of_states = 0
    
    def set_input_states(self,dic_input_state):
        self.dic_input_state = dic_input_state
        
        self._set_converter_matrix()
    
    def set_perturbednode_states(self, dic_perturbednode_state):
        self.dic_perturbednode_state = dic_perturbednode_state
        
        self._set_converter_matrix()
    
    def set_order_of_nodes(self, l_order):
        self.l_order_nodes = l_order
        
        self._set_converter_matrix()
    
    def _set_converter_matrix(self):
        if not self.l_order_nodes:
            return
        else:
            self.array_converter_state_to_integer = _get_array_converter_state_to_int(self.l_order_nodes, 
                                                                                      self.dic_input_state, 
                                                                                      self.dic_perturbednode_state)
            
            self.matrix_converter_chagable_to_all = _matrix_converter_from_changable_to_all_state(self.l_order_nodes, 
                                                                                      self.dic_input_state, 
                                                                                      self.dic_perturbednode_state)
            
            self.array_not_changed_state = _array_perturbed_state_input_state(self.l_order_nodes, 
                                                                            self.dic_input_state, 
                                                                            self.dic_perturbednode_state)
            
            self.i_num_changing_nodes = len(self.l_order_nodes) - len(self.dic_input_state) - len(self.dic_perturbednode_state)
            
    def add_state(self,array_state):
        i_before = self.ifs_states.show_integer_form()
        self.ifs_states += np.dot(array_state, self.array_converter_state_to_integer)
        if self.ifs_states.show_integer_form() != i_before:
            self.i_num_of_states += 1
        
    def add_state_integer_form(self, i_state):
        i_before = self.ifs_states.show_integer_form()
        self.ifs_states += i_state
        if self.ifs_states.show_integer_form() != i_before:
            self.i_num_of_states += 1
    
    def union_basin(self,basin_to_add):
        if self.show_order_of_states() != basin_to_add.show_order_of_states():
            print("node order of added basin is ", self.show_order_of_states())
            print("node order of adding basing is", basin_to_add.show_order_of_states())
            raise ValueError("two basins have different node order!")
        if self.show_input_states() != basin_to_add.show_input_states():
            print("input nodes of added basin is ", self.show_input_states())
            print("input nodes of adding basing is", basin_to_add.show_input_states())
            raise ValueError("two basins have different input states!")
        if self.show_perturbed_states() != basin_to_add.show_perturbed_states():
            print("perturbed nodes of added basin is ", self.show_perturbed_states())
            print("perturbed nodes adding basing is", basin_to_add.show_perturbed_states())
            raise ValueError("two basins have different perturbed states")
            
        self.ifs_states.union(basin_to_add._show_ifs(), b_update=True)
        
    def has_the_state(self, array_state):
        return self.ifs_states.has_the_number(np.dot(array_state, self.array_converter_state_to_integer))
    
    def has_the_state_integer_form(self, i_state):
        return self.ifs_states.has_the_number(i_state)
    
    def show_order_of_states(self):
        return self.l_order_nodes
    
    def show_input_states(self):
        return self.dic_input_state
    
    def show_perturbed_states(self):
        return self.dic_perturbednode_state
    
    def show_all_states_list_form(self):
        return [self._integer_to_state(i_state) for i_state in self.ifs_states.as_generator()]
    
    def show_states_except_attractor_list_form(self):
        ifs_except_attractor = DSM.Integer_form_numberset(self.ifs_states.show_integer_form())
        for i_state in self.l_i_attractor:
            ifs_except_attractor -= i_state
        return [self._integer_to_state(i_state) for i_state in ifs_except_attractor.as_generator()]
    
    def show_all_states_generator(self):
        return (self._integer_to_state(i_state) for i_state in self.ifs_states.as_generator())
    
    def show_states_except_attractor_generator(self):
        ifs_except_attractor = DSM.Integer_form_numberset(self.ifs_states.show_integer_form())
        for i_state in self.l_i_attractor:
            ifs_except_attractor -= i_state
        return (self._integer_to_state(i_state) for i_state in ifs_except_attractor.as_generator())
    
    def show_one_state(self):
        i_state = self.ifs_states.show_smallest_element()
        return self._integer_to_state(i_state)
    
    def _integer_to_state(self, i_state):
        array_changing_states = np.array(list(("{:>0%d}" %self.i_num_changing_nodes).format(bin(i_state)[2:])), dtype=int)
        array_all = np.matmul(array_changing_states, self.matrix_converter_chagable_to_all) + self.array_not_changed_state
        return array_all
    
    def _show_ifs(self):
        return self.ifs_states
        
    def add_attractor(self, l_attractor):
        for array_state in l_attractor:
            i_state = np.dot(array_state, self.array_converter_state_to_integer)
            self.l_i_attractor.append(i_state)
            self.add_state_integer_form(i_state)
    
    def add_attractor_integer_form(self, l_i_attractor):
        self.l_i_attractor = l_i_attractor
        for i_state in self.l_i_attractor:
            self.add_state_integer_form(i_state)
    
    def show_attractor(self):
        return [self._integer_to_state(i_state) for i_state in self.l_i_attractor]
    
    def is_point_attractor(self):
        if not self.l_i_attractor:# self.l_i_attractor == []
            raise ValueError("attractor is not yet entered")
        return len(self.l_i_attractor) == 1
    
    

                
        
        
        
