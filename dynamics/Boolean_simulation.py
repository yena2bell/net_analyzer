# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 19:06:56 2019

@author: jwKim
"""
import numpy as np
import random

from . import dynamics_supporting_module as DSM
from . import Boolean_functions

class Dynamics_condition_data:
    def __init__(self, network):
        self.network_to_simulate = network
        self.ls_nodename_order = []
        self.ls_input_nodename = []
        self.dic_nodename_i_truthtable = {}
        self.dic_nodename_l_regulatorsname_orderd = {}
        self.dic_nodename_matrix_regulatorinfo = {}
        self.l_t_s_node_i_position_not_input_not_perturbed = [] #[(nodename, index in all node list),,,]
        self._extract_dynamics_information_from_network()
        
        self.dic_inputnode_state = {}
        self.dic_perturbednode_state = {}
        
        self.s_object_name = "dynamics_data_of_"+str(network)
        
    def __repr__(self):
        return self.s_object_name
        
    def _extract_dynamics_information_from_network(self):
        l_nodes_input = self.network_to_simulate.show_input_nodes()
        self.ls_input_nodename = [str(node) for node in l_nodes_input]
        
        l_nodes_not_input = self.network_to_simulate.show_not_input_nodes()
        ls_not_input_nodename = [str(node) for node in l_nodes_not_input]
        self.ls_nodename_order = self.ls_input_nodename + ls_not_input_nodename
        
        self.l_t_s_node_i_position_not_input_not_perturbed = [(s_nodename,self.ls_nodename_order.index(s_nodename)) for s_nodename in ls_not_input_nodename]
        
        
        for node in l_nodes_input+l_nodes_not_input:
            i_truthtable = node.show_integerform_of_Boolean_truthtable()
            if i_truthtable == None:
                if node.is_source_node():
                    continue
                elif node.is_input_node():#input node but not source node
                    self.s_object_name +='\n'
                    self.s_object_name += "caution: input node "+str(node)+" has no logic"
                else:
                    raise ValueError(str(node)+" logic information is not entered!")
            else:
                self.dic_nodename_i_truthtable[str(node)] = node.show_integerform_of_Boolean_truthtable()
                
                ls_regulators_ordered = node.show_orderedname_regulators_truthtable()
                self.dic_nodename_l_regulatorsname_orderd[str(node)] = ls_regulators_ordered
                
                li_regulators_ordered = [self.ls_nodename_order.index(nodename) for nodename in ls_regulators_ordered]
                matrix_regulator_info = np.array([[0]*len(li_regulators_ordered)]*len(self.ls_nodename_order))
                for i_column, i_row in enumerate(li_regulators_ordered):
                    matrix_regulator_info[i_row, i_column] = 1
                self.dic_nodename_matrix_regulatorinfo[str(node)] = matrix_regulator_info
    
    def set_perturbation(self, dic_perturbednode_state):
        self.dic_perturbednode_state = dic_perturbednode_state
        
        for s_node_perturbed in self.dic_perturbednode_state.keys():
            ls_node_not_input_not_perturbed = self.show_nodenames_changable_ordered()
            i_position = ls_node_not_input_not_perturbed.index(s_node_perturbed)
            self.l_t_s_node_i_position_not_input_not_perturbed.pop(i_position)
    
    def set_input_condition(self,dic_or_array_form_input_condition):
        if type(dic_or_array_form_input_condition) == type({}):
            if set(self.ls_input_nodename) != set(dic_or_array_form_input_condition.keys()):
                print("Error raised in input condition setting")
                raise ValueError(str(dic_or_array_form_input_condition)+"has missing input node")
            else:
                self.dic_inputnode_state = dic_or_array_form_input_condition
        else:
            if len(dic_or_array_form_input_condition) != len(self.ls_input_nodename):
                print("Error raised in input condition setting")
                raise ValueError("inserted input state has "+str(len(dic_or_array_form_input_condition))+" element. it should be "+str(len(self.ls_input_nodename))+" elements")
            else:
                for i, element in enumerate(dic_or_array_form_input_condition):
                    if type(element) == type("string"):
                        dic_or_array_form_input_condition[i] = int(element)
                self.dic_inputnode_state = dict(zip(self.ls_input_nodename, dic_or_array_form_input_condition))
    
    def show_nodename_order(self):
        return self.ls_nodename_order
    
    def show_dict_nodename_Boolean_truthtable(self):
        return self.dic_nodename_i_truthtable
    
    def show_dict_nodename_regulator_order(self):
        return self.dic_nodename_l_regulatorsname_orderd
    
    def show_input_condition(self):
        return self.dic_inputnode_state
    
    def show_perturbation(self):
        return self.dic_perturbednode_state
    
    def show_nodenames_changable_ordered(self):
        return [t[0] for t in self.l_t_s_node_i_position_not_input_not_perturbed]
    
    def show_number_of_changale_nodes(self):
        return len(self.l_t_s_node_i_position_not_input_not_perturbed)
    
    def update_changable_node_states(self, array_state_all):
        """array_state_all = concatenateion  of array_input_state and array_not_input_state
        perturbation effect is in dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo"""
        array_next = array_state_all.copy()
        
        for s_node_changable, i_position in self.l_t_s_node_i_position_not_input_not_perturbed:
            array_state_regulator = np.matmul(array_state_all, self.dic_nodename_matrix_regulatorinfo[s_node_changable])
            array_next[i_position] = Boolean_functions.Boolean_function(self.dic_nodename_i_truthtable[s_node_changable], array_state_regulator)
        
        return array_next
    
    def apply_input_condition(self, array_state_all):
        array_state_new = array_state_all.copy()
        for s_inputnodename in self.ls_input_nodename:
            i_position = self.ls_nodename_order.index(s_inputnodename)
            array_state_new[i_position] = self.dic_inputnode_state[s_inputnodename]
        
        return array_state_new
    
    def apply_perturbation(self, array_state_all):
        array_state_new = array_state_all.copy()
        for s_perturbednodename in self.dic_perturbednode_state.keys():
            i_position = self.ls_nodename_order.index(s_perturbednodename)
            array_state_new[i_position] = self.dic_perturbednode_state[s_perturbednodename]
        
        return array_state_new
    
        
def attractor_basin_calculation_for_specific_perturbation(network_object,
                                                dic_perturbednode_state):
    """use Boolean synchronous update
    lt_s_nodename_i_perturbedstate = [(nodename, 1 or 0), (nodename, True of False),,,]
    if b_combine_output_in_one_file == True, outputs for each input_condition will be written in one file."""
    
    l_nodes_input = network_object.show_input_nodes()
    ls_inputnodenames = [str(node) for node in l_nodes_input]
   
    for s_inputnode in ls_inputnodenames:
        if s_inputnode in dic_perturbednode_state.keys():
            raise ValueError(s_inputnode+" is input node but perturbed")
    
    dic_i_inputcondition_l_basin = {}
    if ls_inputnodenames:
        for i_inputcondition in range(pow(2,len(ls_inputnodenames))):
            array_inputcondition = DSM.int_to_arraystate(i_inputcondition, len(ls_inputnodenames))
            dic_input_state = dict(zip(ls_inputnodenames, array_inputcondition))
            print(dic_input_state, " input condition calculation starts")
            l_basin = attractor_basin_calculation_for_specific_inputcondition_perturbation(network_object,
                                                                                           dic_input_state,
                                                                                           dic_perturbednode_state)
            dic_i_inputcondition_l_basin[i_inputcondition] = l_basin
    else:
        print("calculation start")
        dic_input_state = {}
        l_basin = attractor_basin_calculation_for_specific_inputcondition_perturbation(network_object,
                                                                                       dic_input_state,
                                                                                       dic_perturbednode_state)
        dic_i_inputcondition_l_basin[-1] = l_basin

    #input condition == -1 means no input nodes.
    #attractor calculation for each basin
    return dic_i_inputcondition_l_basin
        

def attractor_basin_calculation_for_specific_inputcondition_perturbation(network_object,
                                                                         dic_input_state,
                                                                         dic_perturbed_state):
    
    dynamics_data = Dynamics_condition_data(network_object)
    dynamics_data.set_perturbation(dic_perturbed_state)
    dynamics_data.set_input_condition(dic_input_state)
    
    ifs_all = DSM.Integer_form_numberset(0)#set of all states calculated.
    l_basin = []
   
    for i in range(pow(2,dynamics_data.show_number_of_changale_nodes())):
        if ifs_all.has_the_number(i):#check whether this state is already calculated.
            continue
        else:
            basin_new = Basin_states(dynamics_data)
            i_next = i
            l_trajectory = []
            array_all = basin_new._integer_to_state(i_next)
            while not ifs_all.has_the_number(i_next):
                ifs_all += i_next
                l_trajectory.append(i_next)
                array_all = dynamics_data.update_changable_node_states(array_all)
                i_next = basin_new._state_to_integer(array_all)
                
            for basin in l_basin:
                if basin.has_the_state_integer_form(i_next):
                    for i_state in l_trajectory:
                        basin.add_state_integer_form(i_state)
                    break
            else:
                l_i_attractor = l_trajectory[l_trajectory.index(i_next):]
                basin_new.add_attractor_integer_form(l_i_attractor)
                for i_state in l_trajectory:
                    basin_new.add_state_integer_form(i_state)
                l_basin.append(basin_new)
                
    return l_basin


def attractor_calculation_for_specific_inputcondition_perturbation(network_object,
                                                                   dic_input_state,
                                                                   dic_perturbed_state,
                                                                   initial_state=None,
                                                                   random_seed=None):
    """if initial_state is None, choose initial state randomly
    input condition and state of perturbed node in initial state is changed 
    according to dic_input_state and dic_perturbed_state before calculation"""
    dynamics_data = Dynamics_condition_data(network_object)
    dynamics_data.set_perturbation(dic_perturbed_state)
    dynamics_data.set_input_condition(dic_input_state)
    
    if type(initial_state) == type(None):
        if random_seed != None:
            random.seed(random_seed)
        i_num_of_nodes = len(dynamics_data.show_nodename_order())
        i_random = random.randint(0, pow(2,i_num_of_nodes)-1)#randint contains pow(2,i_num_of_nodes)-1
        initial_state = DSM.int_to_arraystate(i_random, i_num_of_nodes)
    
    dic_initial_state = dict(zip(dynamics_data.show_nodename_order(), initial_state))
    for s_input in dic_input_state.keys():
        dic_initial_state[s_input] = dic_input_state[s_input]
    for s_perturbed in dic_perturbed_state.keys():
        dic_initial_state[s_perturbed] = dic_perturbed_state[s_perturbed]
    print("calculate attractor starting at ",dic_initial_state)
    
    object_attractor = _attractor_calculation(dynamics_data, initial_state)
    
    return object_attractor

def _attractor_calculation(dynamics_data, initial_state):
    """apply input condition and perturbaion to initial state, and find attractor of that initial state
    initial state is array or list form state which has states of all nodes"""
    object_attractor = Attractor_synchronous_Boolean(dynamics_data)
    l_trajectory = []
    array_state = np.array(initial_state, dtype=int)#convert list or tuple to numpy array
    array_state = dynamics_data.apply_input_condition(array_state)
    array_state = dynamics_data.apply_perturbation(array_state)
    i_state = object_attractor._state_to_integer(array_state)
    while not (i_state in l_trajectory):
        l_trajectory.append(i_state)
        array_state = dynamics_data.update_changable_node_states(array_state)
        i_state = object_attractor._state_to_integer(array_state)
    
    l_i_attractor = l_trajectory[l_trajectory.index(i_state):]
    object_attractor.add_attractor_integer_form(l_i_attractor)
    
    return object_attractor


def attractors_calculation_from_ramdom_initial_states_iteratively(network_object,
                                                                  dic_input_state,
                                                                  dic_perturbed_state={},
                                                                  i_maximum_interval_without_new_att=10000,
                                                                  i_maximum_calculation=None,
                                                                  i_random_seed=None):
    """if i_maximum_calculation=None, then i_maximum_calculation is 1/10 of all initial states"""
    dynamics_data = Dynamics_condition_data(network_object)
    dynamics_data.set_perturbation(dic_perturbed_state)
    dynamics_data.set_input_condition(dic_input_state)
    converter_info = Object_state_saving_integer_form(dynamics_data)
    i_all_initial_changable = pow(2,dynamics_data.show_number_of_changale_nodes())
    
    if type(i_random_seed) != type(None):
        random.seed(i_random_seed)
    if type(i_maximum_calculation) == type(None):
        i_maximum_calculation = int(i_all_initial_changable/10)
        
    ifs_initials_calculated = DSM.Integer_form_numberset(0)
    l_attractors = []
    li_count_new_att = [0]#for error proof in (i_count - li_count_new_att[-1]) code (while argument)
    i_count = 0 #the number of initial states calculated.
    
    while (i_count <= i_maximum_calculation) and ((i_count - li_count_new_att[-1]) <= i_maximum_interval_without_new_att):
        i_initial = random.randrange(0,i_all_initial_changable)
        if ifs_initials_calculated.has_the_number(i_initial):
            continue
        else:
            i_count += 1
            ifs_initials_calculated += i_initial
            array_initial = converter_info._integer_to_state(i_initial)
            obj_attractor = _attractor_calculation(dynamics_data, array_initial)
            if not obj_attractor in l_attractors:
                l_attractors.append(obj_attractor)
                li_count_new_att.append(i_count)
                print("new attractor discovered! at ",i_count,"th calculation")
    
    li_count_new_att.pop(0)#deletion initial 0 value
    return l_attractors, li_count_new_att
    
    
class Object_state_saving_integer_form:
    def __init__(self, dynamics_data):
        self.dynamics_data = dynamics_data
        
        self.array_converter_state_to_integer = None
        self.matrix_converter_chagable_to_all = None
        self.array_not_changed_state = None
        self._set_converter_matrix()
        
    def _set_converter_matrix(self):
        self._get_array_converter_state_to_int()#calculate self.array_converter_state_to_integer
        self._matrix_converter_from_changable_to_all_state()#calculate self.matrix_converter_chagable_to_all
        self._array_perturbed_state_input_state()#calculate self.array_not_changed_state
        
    def _integer_to_state(self, i_state):
        """i_state is integer form of state of only changable nodes"""
        array_changing_states = np.array(list(("{:>0%d}" %self.dynamics_data.show_number_of_changale_nodes()).format(bin(i_state)[2:])), dtype=np.int64)
        array_all = np.matmul(array_changing_states, self.matrix_converter_chagable_to_all) + self.array_not_changed_state
        return array_all
    
    def _state_to_integer(self, array_state):
        return np.dot(array_state, self.array_converter_state_to_integer)
    
    def _get_array_converter_state_to_int(self):
        l_order_nodenames = self.dynamics_data.show_nodename_order()
        dic_input_state = self.dynamics_data.show_input_condition()
        dic_perturbed_state = self.dynamics_data.show_perturbation()
    
        i_num_changing_nodes = self.dynamics_data.show_number_of_changale_nodes()
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
        
        self.array_converter_state_to_integer = np.array(l_tmp, dtype=np.int64)
    
    def _matrix_converter_from_changable_to_all_state(self):
        """when ls_not_inputnodenames = [a,b,c,d,e,f], and dic_s_nodename_i_perturbedstate = {b:0, e:1}
        array_perturbed_state = array([0,0,0,0,1,0])
        matrix_converter is 4*6 matrix. 
        if (a,c,e,f) = (1,0,1,0), then (1,0,1,0 ) @ matrix_converter + array_perturbed_state = (1,0,0,1,1,0)
        it can be used to make overall state from not perturbed nodes state"""
        l_order_nodenames = self.dynamics_data.show_nodename_order()
        dic_input_state = self.dynamics_data.show_input_condition()
        dic_perturbed_state = self.dynamics_data.show_perturbation()
    
        i_num_changing_nodes = self.dynamics_data.show_number_of_changale_nodes()
        l_index_inputs = []
        for s_node in dic_input_state.keys():
            l_index_inputs.append(l_order_nodenames.index(s_node))
        l_index_perturbed = []
        for s_node in dic_perturbed_state.keys():
            l_index_perturbed.append(l_order_nodenames.index(s_node))
        l_index_no_change = l_index_inputs+l_index_perturbed
        
        matrix_converter = np.array([[0]*len(l_order_nodenames)]*i_num_changing_nodes, dtype=np.int64)
        i_row = 0
        for i_column in range(len(l_order_nodenames)):
            if i_column not in l_index_no_change:
                matrix_converter[i_row][i_column] = 1
                i_row += 1
        
        self.matrix_converter_chagable_to_all = matrix_converter
    
    def _array_perturbed_state_input_state(self):
        l_order_nodenames = self.dynamics_data.show_nodename_order()
        dic_input_state = self.dynamics_data.show_input_condition()
        dic_perturbed_state = self.dynamics_data.show_perturbation()
    
        l_tmp = [0]*len(l_order_nodenames)
        for s_input in dic_input_state.keys():
            l_tmp[l_order_nodenames.index(s_input)] = dic_input_state[s_input]
        for s_perturbed in dic_perturbed_state.keys():
            l_tmp[l_order_nodenames.index(s_perturbed)] = dic_perturbed_state[s_perturbed]
        
        self.array_not_changed_state = np.array(l_tmp, dtype=np.int64)
        
    def show_nodename_order(self):
        return self.dynamics_data.show_nodename_order()

    def show_input_condition(self):
        return self.dynamics_data.show_input_condition()
    
    def show_perturbation(self):
        return self.dynamics_data.show_perturbation()
    
    def show_nodenames_changable_ordered(self):
        return self.dynamics_data.show_nodenames_changable_ordered()

class Basin_states(Object_state_saving_integer_form):
    def __init__(self, dynamics_data):
        Object_state_saving_integer_form.__init__(self, dynamics_data)
        self.ifs_states = DSM.Integer_form_numberset(0)
        self.i_num_changing_nodes = self.dynamics_data.show_number_of_changale_nodes()
        self.object_attractor = Attractor_synchronous_Boolean(dynamics_data)
        self.i_num_of_states = 0

    def add_state(self,array_state):
        i_before = self.ifs_states.show_integer_form()
        self.ifs_states += self._state_to_integer(array_state)
        if self.ifs_states.show_integer_form() != i_before:
            self.i_num_of_states += 1
        
    def add_state_integer_form(self, i_state):
        i_before = self.ifs_states.show_integer_form()
        self.ifs_states += i_state
        if self.ifs_states.show_integer_form() != i_before:
            self.i_num_of_states += 1
    
    def union_basin(self,basin_to_add):
        if self.dynamics_data != basin_to_add.dynamics_data:
            print("Error in Basin union function")
            raise ValueError("dynamics_data of two basin object are different!")
            
        self.ifs_states.union(basin_to_add._show_ifs(), b_update=True)
        
    def has_the_state(self, array_state):
        return self.ifs_states.has_the_number(self._state_to_integer(array_state))
    
    def has_the_state_integer_form(self, i_state):
        return self.ifs_states.has_the_number(i_state)

    def show_all_states_list_form(self):
        return [self._integer_to_state(i_state) for i_state in self.ifs_states.as_generator()]
    
    def show_states_except_attractor_list_form(self):
        ifs_except_attractor = DSM.Integer_form_numberset(self.ifs_states.show_integer_form())
        for i_state in self.object_attractor.show_attractor_integer_form():
            ifs_except_attractor -= i_state
        return [self._integer_to_state(i_state) for i_state in ifs_except_attractor.as_generator()]
    
    def show_all_states_generator(self):
        return (self._integer_to_state(i_state) for i_state in self.ifs_states.as_generator())
    
    def show_states_except_attractor_generator(self):
        ifs_except_attractor = DSM.Integer_form_numberset(self.ifs_states.show_integer_form())
        for i_state in self.object_attractor.show_attractor_integer_form():
            ifs_except_attractor -= i_state
        return (self._integer_to_state(i_state) for i_state in ifs_except_attractor.as_generator())
    
    def show_one_state(self):
        i_state = self.ifs_states.show_smallest_element()
        return self._integer_to_state(i_state)
    
    def _show_ifs(self):
        return self.ifs_states
    
    def show_number_of_states_in_basin(self):
        return self.i_num_of_states
    
    def has_point_attractor(self):
        return self.object_attractor.is_point_attractor()
    
    def add_attractor_state_form(self, larray_attractor):
        self.object_attractor.add_attractor(larray_attractor)
        for array_state in larray_attractor:
            self.add_state(array_state)
    
    def add_attractor_integer_form(self, li_attractor):
        self.object_attractor.add_attractor_integer_form(li_attractor)
        for i_state in li_attractor:
            self.add_state_integer_form(i_state)
    
    def show_attractor(self):
        return self.object_attractor.show_attractor()
    
    def show_attractor_integer_form(self):
        return self.object_attractor.show_attractor_integer_form()
        

class Attractor_synchronous_Boolean(Object_state_saving_integer_form):
    def __init__(self, dynamics_data):
        Object_state_saving_integer_form.__init__(self, dynamics_data)
        self.l_i_attractor = []
    
    def show_attractor(self):
        return [self._integer_to_state(i_state) for i_state in self.l_i_attractor]
    
    def show_attractor_integer_form(self):
        return self.l_i_attractor
    
    def is_point_attractor(self):
        if not self.l_i_attractor:# self.l_i_attractor == []
            raise ValueError("attractor is not yet entered")
        return len(self.l_i_attractor) == 1
    
    def add_attractor(self, larray_attractor):
        for array_state in larray_attractor:
            i_state = self._state_to_integer(self, array_state)
            self.l_i_attractor.append(i_state)
            self.add_state_integer_form(i_state)
    
    def add_attractor_integer_form(self, l_i_attractor):
        self.l_i_attractor = l_i_attractor
        
    def __eq__(self, other):
        if type(other) != type(self):
            raise ValueError("this is not attractor object")
            
        if len(self.l_i_attractor) == 0:
            raise ValueError("attractor states are not yet set")
        if len(other.l_i_attractor) == 0:
            raise ValueError("attractor states are not yet set")
            
        if len(self.l_i_attractor) != len(other.l_i_attractor):
            return False
        else:
            if other.dynamics_data.show_nodename_order() != self.dynamics_data.show_nodename_order():
                if set(other.dynamics_data.show_nodename_order()) != set(self.dynamics_data.show_nodename_order()):
                    print("two attractors come from different network model(different node names)")
                    return False
                else: #convert other's attractor state order to self's attractor state order
                    l_array_attractor_other = other.show_attractor()
                    i_num_of_nodes = other.dynamics_data.show_nodename_order()
                    matrix_converter_between_two_attractors = np.zeros((i_num_of_nodes,i_num_of_nodes))
                    for j in range(i_num_of_nodes):
                        s_node_jth_in_self = self.dynamics_data.show_nodename_order()[j]
                        i = other.dynamics_data.show_nodename_order().index(s_node_jth_in_self)
                        matrix_converter_between_two_attractors[i,j] = 1
                    l_array_attractor_other = [np.matmul(array_state, matrix_converter_between_two_attractors) for array_state in l_array_attractor_other]
            else:
                l_array_attractor_other = other.show_attractor()
                
            l_array_attractor_self = self.show_attractor()
            for i, array_state in enumerate(l_array_attractor_self):
                if (l_array_attractor_other[0] == array_state).all():
                    l_array_attractor_self = l_array_attractor_self[i:]+l_array_attractor_self[:i]
                    if (np.array(l_array_attractor_other) == np.array(l_array_attractor_self)).all():
                        return True
                    else:
                        return False
            return False