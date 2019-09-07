# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 19:06:56 2019

@author: jwKim
"""
import numpy as np
import os, time

from . import dynamics_supporting_module as DSM
from ..support_functions.folder_functions import directory_making
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
    
    return ls_inputnodenames, ls_not_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo
    
        
def basin_calculation_for_specific_perturbation(ls_inputnodenames, 
                                                ls_not_inputnodenames, 
                                                dic_nodename_i_truthtable, 
                                                dic_nodename_array_regulatorinfo, 
                                                lt_s_nodename_i_perturbedstate, 
                                                s_address_folder_output, 
                                                b_combine_output_in_one_file = False):
    """use Boolean synchronous update
    lt_s_nodename_i_perturbedstate = [(nodename, 1 or 0), (nodename, True of False),,,]
    if b_combine_output_in_one_file == True, outputs for each input_condition will be written in one file."""
    

    
    #making folder for output files 
    s_foldername_for_output = time.strftime("%Y%m%d_%Hhour%Mmin%Ssec",time.localtime(time.time()))
    if not lt_s_nodename_i_perturbedstate:
        s_foldername_for_output += "_no_perturbation"
    else:
        for t_node_state in lt_s_nodename_i_perturbedstate:
            s_foldername_for_output += '_'+str(t_node_state[0])+'_'+str(t_node_state[1])
    s_address_folder_output = os.path.join(s_address_folder_output, s_foldername_for_output)
    directory_making(s_address_folder_output)
    
    #check the lt_s_nodename_i_perturbedstate. and convert it to dic_snode_perturbed
    dic_snode_perturbed = dict(lt_s_nodename_i_perturbedstate)#key is perturbed node, value is perturbed state
    if len(dic_snode_perturbed) != len(lt_s_nodename_i_perturbedstate):
        raise ValueError("there are duplication in perturbation argument")
    for s_inputnode in ls_inputnodenames:
        if s_inputnode in dic_snode_perturbed.keys():
            raise ValueError(s_inputnode+" is input node but perturbed")

    #write dynamics info text file. it contains input nodes, perturbed nodes, and perturbed state
    write_dynamics_information(os.path.join(s_address_folder_output,"dynamics_info.txt"), ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed)
    
    #modify dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo to reflect modification
    for s_node_perturbed in dic_snode_perturbed.keys():
        if dic_snode_perturbed[s_node_perturbed]:#perturbed to 1 or True
            dic_nodename_i_truthtable[s_node_perturbed] = 1
        else:
            dic_nodename_i_truthtable[s_node_perturbed] = 0
        dic_nodename_array_regulatorinfo[s_node_perturbed] = np.array([[0]*0]*(len(ls_inputnodenames)+len(ls_not_inputnodenames)))
    
    #make perturbation information as array_perturbed_state and matrix_converter
    array_perturbed_state, matrix_converter = perturbed_state_combining_matrix_and_state(ls_not_inputnodenames, dic_snode_perturbed)
    
    #calculate basins for each input condition. and summarize basin information as integer_form_set.
    dic_i_inputcondition_l_integerformsets = {}
    if ls_inputnodenames:
        for i_inputcondition in range(pow(2,len(ls_inputnodenames))):
            array_inputcondition = DSM.int_to_arraystate(i_inputcondition, len(ls_inputnodenames))
            print(i_inputcondition, " input condition calculation starts")
            l_integerformset = basin_calculation_for_specific_inputcondition_and_perturbation(ls_inputnodenames, 
                                                                           ls_not_inputnodenames, 
                                                                           dic_nodename_i_truthtable, 
                                                                           dic_nodename_array_regulatorinfo, 
                                                                           array_perturbed_state, 
                                                                           matrix_converter,
                                                                           array_inputcondition)
            dic_i_inputcondition_l_integerformsets[i_inputcondition] = l_integerformset
    
    else:#no input nodes
        array_inputcondition = np.array([])
        print("calculation start")
        l_integerformset = basin_calculation_for_specific_inputcondition_and_perturbation(ls_inputnodenames, 
                                                                       ls_not_inputnodenames, 
                                                                       dic_nodename_i_truthtable, 
                                                                       dic_nodename_array_regulatorinfo, 
                                                                       array_perturbed_state, 
                                                                       matrix_converter,
                                                                       array_inputcondition)
        dic_i_inputcondition_l_integerformsets[-1] = l_integerformset
    
    #input condition == -1 means no input nodes.
    #attractor calculation for each basin
    dic_i_inputcondition_l_l_att = {}
    for i_inputcondition in dic_i_inputcondition_l_integerformsets.keys():
        ll_atts = []
        for ifs_basin in dic_i_inputcondition_l_integerformsets[i_inputcondition]:
            i_state = ifs_basin.show_smallest_element()#i_state don't contain input states and perturbed states
            if i_inputcondition == -1:
                array_state_all = DSM.int_to_arraystate(i_state, len(matrix_converter)) @ matrix_converter + array_perturbed_state
            else:
                array_state_all = np.concatenate([DSM.int_to_arraystate(i_inputcondition, len(ls_inputnodenames)),
                                              DSM.int_to_arraystate(i_state, len(matrix_converter)) @ matrix_converter + array_perturbed_state])
            l_att = find_attractor_of_initial_state(ls_inputnodenames,
                                                    ls_not_inputnodenames, 
                                                    dic_nodename_i_truthtable, 
                                                    dic_nodename_array_regulatorinfo, 
                                                    array_state_all)
            ll_atts.append(l_att)
        dic_i_inputcondition_l_l_att[i_inputcondition] = ll_atts
    #dic_i_inputcondition_l_integerformsets[i][j] basin has dic_i_inputcondition_l_l_att[i][j] attractor value
    #be careful! integer in ifs_basin is state of not input and not perturbed
    #but integer in l_att is state of all nodes
    #delete states in attractor from basin set. it is for printout function.
    for i_inputcondition in dic_i_inputcondition_l_integerformsets.keys():
        for i, l_att in enumerate(dic_i_inputcondition_l_l_att[i_inputcondition]):
            for i_state in l_att:
                array_state = DSM.int_to_arraystate(i_state, (len(ls_inputnodenames)+ len(ls_not_inputnodenames)))
                i_state_modified = DSM.arraystate_to_int(array_state[-len(ls_not_inputnodenames):] @ matrix_converter.transpose())
                dic_i_inputcondition_l_integerformsets[i_inputcondition][i] -= i_state_modified

    #printout code
    if b_combine_output_in_one_file: #print out all results in one file.
        pass
    else:
        for i_inputcondition in dic_i_inputcondition_l_integerformsets.keys():
            if i_inputcondition == -1:
                s_filename_basin = "att_basin_perturbed.tsv"
                s_filename_atts = "attractor_information.txt"
                array_input_state = np.array([])
            else:
                s_filename_basin = "att_basin_perturbed_on_input_condition_{}.tsv".format(i_inputcondition)
                s_filename_atts = "attractor_information_on_input_condition_{}.txt".format(i_inputcondition)
                array_input_state = DSM.int_to_arraystate(i_inputcondition, len(ls_inputnodenames))
                
            s_address_basin = os.path.join(s_address_folder_output, s_filename_basin)
            s_address_atts = os.path.join(s_address_folder_output, s_filename_atts)
            ll_atts = []
            write_output_header(s_address_basin, ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed)
            for i_code, ifs_basin in enumerate(dic_i_inputcondition_l_integerformsets[i_inputcondition]):
                l_i_state_att = dic_i_inputcondition_l_l_att[i_inputcondition][i_code]
                l_atts = [DSM.int_to_arraystate(i_state, len(ls_inputnodenames)+len(ls_not_inputnodenames)) for i_state in l_i_state_att]
                ll_atts.append(l_atts)
                l_states_in_basin = [np.concatenate([array_input_state,DSM.int_to_arraystate(i_state, len(matrix_converter)) @ matrix_converter + array_perturbed_state]) for i_state in ifs_basin.show_list_form()]
                                
                write_output_one_basin_one_att(s_address_basin, i_code, l_atts, l_states_in_basin)
            write_attractor_information(s_address_atts, ll_atts, ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed)
        

def basin_calculation_for_specific_inputcondition_and_perturbation(ls_inputnodenames, 
                                                               ls_not_inputnodenames, 
                                                               dic_nodename_i_truthtable, 
                                                               dic_nodename_array_regulatorinfo, 
                                                               array_perturbed_state, 
                                                               matrix_converter, 
                                                               array_input_state):
                
    l_integerformset = []
    ifs_all = DSM.Integer_form_numberset(0)#set of all states calculated.
    for i in range(pow(2,len(matrix_converter))):# len(matrix_converter) is the number of node which is not input node and perturbed node
        if ifs_all.has_the_number(i):#check whether this state is already calculated.
            continue
        else:
            i_next = i
            ifs_trajectory = DSM.Integer_form_numberset(0)#set of states in this trajectory, 0 means empty set.
            array_all = np.concatenate([array_input_state, DSM.int_to_arraystate(i_next, len(matrix_converter)) @ matrix_converter + array_perturbed_state])
            while not ifs_all.has_the_number(i_next):
                ifs_trajectory += i_next
                ifs_all += i_next
                array_all = next_state_calculatrion(array_all, ls_not_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo)
                i_next = int(DSM.arraystate_to_int(array_all[-len(ls_not_inputnodenames):] @ matrix_converter.transpose()))
            
            for ifs_others in l_integerformset: # check whether this trajectory is connected alreaed calculated trajectory.
                if ifs_others.has_the_number(i_next):#if connected to already calculted one, union two trajectory
                    ifs_others.union(ifs_trajectory,b_update=True)
                    break
            else:#if there is no intersected trajectory, save this trajectory newly.
                l_integerformset.append(ifs_trajectory)

    return l_integerformset
            
                
            
            

def perturbed_state_combining_matrix_and_state(ls_not_inputnodenames, dic_s_nodename_i_perturbedstate):
    """when ls_not_inputnodenames = [a,b,c,d,e,f], and dic_s_nodename_i_perturbedstate = {b:0, e:1}
    array_perturbed_state = array([0,0,0,0,1,0])
    matrix_converter is 4*6 matrix. 
    if (a,c,e,f) = (1,0,1,0), then (1,0,1,0 ) @ matrix_converter + array_perturbed_state = (1,0,0,1,1,0)
    it can be used to make overall state from not perturbed nodes state"""
    li_position_perturbed = [] #i_position of perturbed nodes on the ls_not_inputnodenames
    array_perturbed_state = np.array([0]*(len(ls_not_inputnodenames)))#perturbation information as array form. 
    for s_node in dic_s_nodename_i_perturbedstate.keys():
        i_position = ls_not_inputnodenames.index(s_node)
        array_perturbed_state[i_position] = dic_s_nodename_i_perturbedstate[s_node]
        li_position_perturbed.append(i_position)
    
    matrix_converter = np.array([[0]*len(ls_not_inputnodenames)]*(len(ls_not_inputnodenames)-len(dic_s_nodename_i_perturbedstate)))
    j=0
    for i in range(len(ls_not_inputnodenames)):
        if i in li_position_perturbed:
            continue
        matrix_converter[j][i] = 1
        j+=1
    
    return array_perturbed_state, matrix_converter


def next_state_calculatrion(array_state_all, ls_not_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo):
    """array_state_all = concatenateion  of array_input_state and array_not_input_state
    perturbation effect is in dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo"""
    array_next = array_state_all.copy()
    ls_not_inputnodenames_reverse = ls_not_inputnodenames[::-1]
    for s_nodename in dic_nodename_i_truthtable.keys():
        i_logic = dic_nodename_i_truthtable[s_nodename]
        matrix_regulator_state = dic_nodename_array_regulatorinfo[s_nodename]
        array_state_regulator = array_state_all @ matrix_regulator_state #sub state of regulators of that node.
        array_next[-(ls_not_inputnodenames_reverse.index(s_nodename)+1)] = Boolean_functions.Boolean_function(i_logic, array_state_regulator)

    return array_next
        
def find_attractor_of_initial_state(ls_inputnodenames,
                                    ls_not_inputnodenames, 
                                    dic_nodename_i_truthtable, 
                                    dic_nodename_array_regulatorinfo,
                                    iorarray_initial_state):
    i_num_node = len(ls_inputnodenames) + len(ls_not_inputnodenames)
    l_i_trajectory = []
    if type(iorarray_initial_state) == type(1):#type int
        i_state = iorarray_initial_state
        array_state = DSM.int_to_arraystate(iorarray_initial_state, i_num_node)
    else:
        iorarray_initial_state = np.array(iorarray_initial_state)#if iorarray_initial_state is list or tuple, convert it array
        i_state = DSM.arraystate_to_int(iorarray_initial_state)
        array_state = iorarray_initial_state

    while i_state not in l_i_trajectory:
        l_i_trajectory.append(i_state)
        array_state = next_state_calculatrion(array_state, ls_not_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo)
        i_state =  DSM.arraystate_to_int(array_state)
    l_i_trajectory.append(i_state)
    
    l_att = l_i_trajectory[l_i_trajectory.index(l_i_trajectory[-1])+1:]
    return l_att

def write_dynamics_information(s_address, ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed):
    with open(s_address, 'w') as file_dynamics_info:
        file_dynamics_info.write("the number of nodes: "+str((len(ls_inputnodenames)+ len(ls_not_inputnodenames))))
        file_dynamics_info.write('\n')
        file_dynamics_info.write("the number of input nodes: "+str(len(ls_inputnodenames)))
        file_dynamics_info.write('\n')
        file_dynamics_info.write("the number of node perturbed: "+str(len(dic_snode_perturbed)))
        file_dynamics_info.write('\n')
        file_dynamics_info.write("type\tname\tperturbed_state")
        for s_nodename in ls_inputnodenames:
            file_dynamics_info.write('\n')
            file_dynamics_info.write("input\t"+s_nodename)
        for s_nodename in ls_not_inputnodenames:
            file_dynamics_info.write('\n')
            s_tmp = ''
            if s_nodename in dic_snode_perturbed.keys():
                file_dynamics_info.write("perturbed\t")
                s_tmp = str(dic_snode_perturbed[s_nodename])
            else:
                file_dynamics_info.write("normal\t")
            file_dynamics_info.write(s_nodename+'\t')
            file_dynamics_info.write(s_tmp)


def write_output_header(s_address, ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed):
    with open(s_address,'a') as file_output:
        file_output.write("\tname")
        for s_node in ls_inputnodenames+ls_not_inputnodenames:
            file_output.write('\t'+s_node)
        file_output.write('\n')
        
        file_output.write("\ttype")
        for s_node in ls_inputnodenames:
            file_output.write("\tinput")
        for s_node in ls_not_inputnodenames:
            if s_node in dic_snode_perturbed.keys():
                file_output.write("\tperturbed")
            else:
                file_output.write("\tnormal")
        file_output.write('\n')
        
        file_output.write("basin_code\tstate_type")
        file_output.write('\n')
        
def write_output_one_basin_one_att(s_address, i_code, l_atts, l_states_in_basin):
    with open(s_address,'a') as file_output:
        for array_state in l_atts:
            file_output.write('\n')
            file_output.write(str(i_code))
            file_output.write('\t')
            file_output.write("att")
            for i in array_state:
                file_output.write('\t')
                file_output.write(str(int(i)))
            
        for array_state in l_states_in_basin:
            file_output.write('\n')
            file_output.write(str(i_code))
            file_output.write('\t')
            file_output.write("normal")
            for i in array_state:
                file_output.write('\t')
                file_output.write(str(int(i)))
                
def write_attractor_information(s_address, ll_atts, ls_inputnodenames, ls_not_inputnodenames, dic_snode_perturbed):
    with open(s_address, 'w') as file_att:
        file_att.write("the number of attractors: ")
        file_att.write(str(len(ll_atts)))
        file_att.write('\n')
        
        ll_pointatt = []
        ll_cyclicatt = []
        for l_att in ll_atts:
            if len(l_att) == 1:
                ll_pointatt.append(l_att)
            else:
                ll_cyclicatt.append(l_att)
        
        file_att.write("the numbor of point attractors: ")
        file_att.write(str(len(ll_pointatt)))
        file_att.write('\n')
        file_att.write("the number of cyclic attractors: ")
        file_att.write(str(len(ll_cyclicatt)))
        file_att.write('\n')
        
        file_att.write("\tname")
        for s_node in ls_inputnodenames+ls_not_inputnodenames:
            file_att.write('\t'+s_node)
        file_att.write('\n')
        
        file_att.write("code\ttype")
        for s_node in ls_inputnodenames:
            file_att.write("\tinput")
        for s_node in ls_not_inputnodenames:
            if s_node in dic_snode_perturbed.keys():
                file_att.write("\tperturbed")
            else:
                file_att.write("\tnormal")
        file_att.write('\n')
        
        i_code = 0
        for l_point in ll_pointatt:
            file_att.write(str(i_code))
            for array_state in l_point:
                file_att.write('\t')
                file_att.write("point")
                for i in array_state:
                    file_att.write('\t')
                    file_att.write(str(int(i)))
                file_att.write('\n')
            i_code+=1
        for l_cycle in ll_cyclicatt:
            file_att.write(str(i_code))
            for array_state in l_cycle:
                file_att.write('\t')
                file_att.write("cycle")
                for i in array_state:
                    file_att.write('\t')
                    file_att.write(str(int(i)))
                file_att.write('\n')
            i_code+=1
        