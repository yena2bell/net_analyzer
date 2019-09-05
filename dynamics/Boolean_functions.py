# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 16:21:36 2019

@author: jwKim
"""
import numpy as np

from .qm import QM

def Boolean_function(i_logic, t_b_inputs):
    """
    t_b_inputs = (True, False, False, True, false)
            ->(1,0,0,1,0)
            -> 1+2*0+4*0+8*1+16*0 = 9
    then this input needs 9+1th line of logic table

    output value in ith line of logic table is
    ith value of binary number of iLogic number
    if iLogic is 25 then binary number is 11001
    then 4th line output is 1 and 3th line output is 0

    element1 element2 element3 output
    0        0        0        a0
    1        0        0        a1
    0        1        0        a2
    1        1        0        a3
    0        0        1        a4
    1        0        1        a5
    0        1        1        a6
    1        1        1        a7

    (1,0,1) has output value in (1+4)+1th line
    i_logic is sum of ai*(2^i)
    
    if t_b_inputs == [],  Boolean_function(0,[]) == False,  Boolean_function(1,[]) == True. 
    """
    
    #check the range of iLogic
    if (pow(2, pow(2,len(t_b_inputs))) <= i_logic) or (i_logic < 0):
        print("logic number range error")
        return

    iLine_position = 0
    for i,bValue in enumerate(t_b_inputs):
        if bValue:
            iLine_position += pow(2,i)

    iLine_output = (i_logic >> iLine_position)%2

    if iLine_output == 1:
        return(True)
    else:
        return(False)
        
        
def output_logictable_of_i_logic(i_logic,i_numofinputs, ts_inputnodes=None):
    """
    output the Boolean logic table of the given i_logic.
    Boolean table is returned by string form.
    output is the string such as
    element1 element2 element3 output
    0        0        0        a0
    1        0        0        a1
    0        1        0        a2
    1        1        0        a3
    0        0        1        a4
    1        0        1        a5
    0        1        1        a6
    1        1        1        a7
    if ts_inputnodes == None, first line shows element1 element2 ....
    if ts_inputnodes == (s_inputnode1, s_inputnode2 ....), first line show these names
    """
    s_table = ''
    if ts_inputnodes:
        for s_inputnode in ts_inputnodes:
            s_table += s_inputnode+'\t'
        s_table += "output\n"
    else:
        for i in range(i_numofinputs):
            s_table += "element{}\t".format(i+1)
        s_table += "output\n"
    
    for i in range(pow(2,i_numofinputs)):
        state = []
        for _ in range(i_numofinputs):
            s_table += "{}\t".format(i%2)
            state.append(i%2)
            i = i >> 1
        s_table += "{}\n".format(Boolean_function(i_logic, state))
    
    return s_table


def get_minimized_Boolean_logic_equation_using_Quine_McCluskey_algorithm_from_truthtable(i_logic, ls_orderd_regulators,b_return_listform=False):
    """convert integer meaning Boolean truth table to minimized Boolean equation (string form)
    ls_orderd_regulators is list of regulator names. it is recommended that regulator name don't have space.
    of course, the order of regulator names is important
    when using b_return_listform=True options, assume that node name don't have space, 'NOT', 'AND', 'OR'"""
    i_num_of_regulators = len(ls_orderd_regulators)
    l_l_states_regulators = [list(("{:0>%d}" %i_num_of_regulators).format(bin(i)[2:])) for i in range(pow(2,i_num_of_regulators))]
    l_l_states_regulators = [[int(i) for i in l_state] for l_state in l_l_states_regulators]
    
    l_i_states_of_regulators = [i for i in range(pow(2,i_num_of_regulators)) if Boolean_function(i_logic, l_l_states_regulators[i])]
    qm = QM(ls_orderd_regulators)
    s_logic_equation = qm.get_function(qm.solve(l_i_states_of_regulators,[])[1])
    if b_return_listform:
        return parse_minimized_Boolean_logic_equation_to_list(s_logic_equation)
    else:
        return s_logic_equation

def parse_minimized_Boolean_logic_equation_to_list(s_logic_equation):
    """this function is for 'get_minimized_Boolean_logic_equation_using_Quine_McCluskey_algorithm_from_truthtable' function.
    parse the string to list form. 
    assume that node name don't have space, 'NOT', 'AND', 'OR'"""
    l_stack = []
    i_position = 0
    i_position_start_of_nodename = 0
    while i_position < len(s_logic_equation):
        if s_logic_equation[i_position] == '(':
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            l_stack.append('(')
            i_position += 1
            i_position_start_of_nodename += 1
            
        elif s_logic_equation[i_position:i_position+3] == "NOT":
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            l_stack.append("NOT")
            i_position += 3
            i_position_start_of_nodename += 3
        elif s_logic_equation[i_position:i_position+3] == "AND":
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            l_stack.append("AND")
            i_position += 3
            i_position_start_of_nodename += 3
        elif s_logic_equation[i_position:i_position+2] == "OR":
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            l_stack.append("OR")
            i_position += 3
            i_position_start_of_nodename += 3
        elif s_logic_equation[i_position] == ' ':
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            i_position += 1
            i_position_start_of_nodename += 1
        elif s_logic_equation[i_position] == ')':       
            if i_position>i_position_start_of_nodename:
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
                i_position_start_of_nodename = i_position
            l_stack.append(')')
            i_position += 1
            i_position_start_of_nodename += 1
        else:
            i_position += 1
            if i_position == len(s_logic_equation):
                l_stack.append(s_logic_equation[i_position_start_of_nodename:i_position])
    return l_stack


def make_multidim_Boolean_function_array(i_logic, i_numofinputs):#I can't remember why I made it
    """make i_numofinputs dimensional array
    array[(i1,i2,i3...)] == Boolean_function(i_logic, (i1,i2,i3,...))
    that array has Boolean value"""
    array_Boolfun_multidim_form = np.zeros((2,)*i_numofinputs, dtype=bool)
    for i in range(pow(2,i_numofinputs)):
        t_coordination = tuple(int(s) for s in reversed(("{0:0%db}"%i_numofinputs).format(i)))
        if Boolean_function(i_logic, t_coordination):
            array_Boolfun_multidim_form[t_coordination] = True
    
    return array_Boolfun_multidim_form
            

def analyze_canalization(i_logic, i_numofinputs):
    """return {1:[('*','1','*'),('1','0','*')], 0:[('0','0','*')]}
    ('1','0','*') in returned dic[1] means that if first input node and second input node has value 1,0 respectively,
    the output node value is canalized to 1"""
    array_Boolean_fun = make_multidim_Boolean_function_array(i_logic, i_numofinputs)
    slice_all = slice(2)#for each dimension, array has 2 elements. so it means all elements of that dimension
    l_1conditions = []
    l_0conditions = []
    for i in range(i_numofinputs):
        t_condition_1 = tuple([slice_all]*i+[1]+[slice_all]*(i_numofinputs-i-1))
        t_condition_0 = tuple([slice_all]*i+[0]+[slice_all]*(i_numofinputs-i-1))
        if array_Boolean_fun[t_condition_1].all():
            l_1conditions.append(tuple(['*']*i+['1']+['*']*(i_numofinputs-i-1)))
        elif  not array_Boolean_fun[t_condition_1].any():
            l_0conditions.append(tuple(['*']*i+['1']+['*']*(i_numofinputs-i-1)))
        if array_Boolean_fun[t_condition_0].all():
            l_1conditions.append(tuple(['*']*i+['0']+['*']*(i_numofinputs-i-1)))
        elif  not array_Boolean_fun[t_condition_0].any():
            l_0conditions.append(tuple(['*']*i+['0']+['*']*(i_numofinputs-i-1)))
    
    return {0:l_0conditions, 1: l_1conditions}