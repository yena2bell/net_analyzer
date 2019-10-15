# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:20:00 2019

@author: jwKim
"""
from ..dynamics import Boolean_functions

class Node:
    def __init__(self, name):
        self.s_name = str(name)
        self.b_issource = False
        self.b_issink = False
        self.l_inwardlinks = [] #automatically appended when link object is created
        self.l_outwardlinks = []#automatically appended when link object is created
        self.tmp = None
        self.dynamics_l_l_order_i_truthtable = None #[[input node1, input node2, ,,,],i_number_making_Boolean_truth_table]
        self.dynamics_s_logicequation = None
        self.Bool_inputnode = False
        self.Bool_outputnode = False
        
    def __repr__(self):
        return self.s_name
    
    def add_inwardlink(self, link):
        self.l_inwardlinks.append(link)
        self.reset_dynamics_information()
        
    def add_outwardlink(self, link):
        self.l_outwardlinks.append(link)
        
    def delete_inwardlink(self, link):
        self.l_inwardlinks.pop(self.l_inwardlinks.index(link))
        self.reset_dynamics_information()
        
    def delete_outwardlink(self, link):
        self.l_outwardlinks.pop(self.l_outwardlinks.index(link))
        
    def show_Boolean_truthtable(self):
        if self.dynamics_l_l_order_i_truthtable:
            i_Boolean_truthtable = self.dynamics_l_l_order_i_truthtable[1]
            l_regulatornames = self.dynamics_l_l_order_i_truthtable[0]
            return Boolean_functions.output_logictable_of_i_logic(i_Boolean_truthtable, len(l_regulatornames), l_regulatornames)
            
        else: #self.dynamics_l_l_order_i_truthtable == None
            print("Boolean truth table information is not inserted")
            
    def show_orderedname_regulators_truthtable(self):
        if self.dynamics_l_l_order_i_truthtable:
            return self.dynamics_l_l_order_i_truthtable[0]
        else:
            if self.show_regulator_nodes():
                print("'show_orderedname_regulators_truthtable' function returns [] but ",str(self)," is not source node.")
            return []
    
    def show_integerform_of_Boolean_truthtable(self):
        if self.dynamics_l_l_order_i_truthtable:
            return self.dynamics_l_l_order_i_truthtable[1]
        else:
            return None

    def reset_dynamics_information(self):
        self.dynamics_l_l_order_i_truthtable = None 
        
    def add_truthtable_integer_form(self, i_truthtable):
        if i_truthtable == None:
            return
        self.dynamics_l_l_order_i_truthtable = [[str(node) for node in self.show_regulator_nodes()],i_truthtable]
        print(str(self)," has new Boolean logic information")
        print(Boolean_functions.output_logictable_of_i_logic(i_truthtable, len(self.show_regulator_nodes()), self.show_orderedname_regulators_truthtable()))
        
    def show_Boolean_logic_equation_form(self):
        return self.dynamics_s_logicequation
    
    def enter_Boolean_logic_equation_form(self, s_Boolean_logic_equation):
        self.dynamics_s_logicequation = str(s_Boolean_logic_equation)
        
    def get_truthtable_integer_form_from_logic_equation(self,**kwargs):
        """default of operation words are as follows
        result='=', OR="OR", AND="AND", NOT="NOT", 
        plus='+', minus='-', biggerequal=">=", 
        bigger='>',smallerequal="<=",smaller='<',equal='=='
        if some changes are needed, write it using keyword arguments"""
        
        dic_operations = {"result":'=', "OR":"or", "AND":"and", "NOT":"not", 
                          "plus":'+', "minus":'-', "multiple":'*',"division":'/',
                          "biggerequal":">=", "bigger":'>',"smallerequal":"<=","smaller":'<',"equal":'=='}
        if kwargs:
            for s_key in kwargs.keys():
                dic_operations[s_key] = kwargs[s_key]
                
        if self.dynamics_s_logicequation == None:
            print("before doing 'get_truthtable_integer_form_from_logic_equation' function, enter the logic_equation(string form) using 'enter_Boolean_logic_equation_form' method")
            return
        elif self.dynamics_s_logicequation[:len(str(self))+1] == str(self)+' ':
            s_logic_equation = self.dynamics_s_logicequation[len(str(self))+1:]
            
        if not self.show_regulator_nodenames():
            print("before doing 'get_truthtable_integer_form_from_logic_equation' function, construct network and make the links with regulator of this node")
            print("if this node is source node, this 'get_truthtable_integer_form_from_logic_equation' method is meaningless")
            return
        i_truthtable, l_order = Boolean_functions.convert_Boolean_logic_equation_to_integer_form_truthtable(s_logic_equation, self.show_regulator_nodenames(),
                                                                                                            result=dic_operations["result"], OR=dic_operations["OR"], AND=dic_operations["AND"], NOT=dic_operations["NOT"], 
                                                                                                            plus=dic_operations["plus"], minus=dic_operations["minus"], biggerequal=dic_operations["biggerequal"], bigger=dic_operations["bigger"],
                                                                                                            smallerequal=dic_operations["smallerequal"],smaller=dic_operations["smaller"],equal=dic_operations["equal"])
        self.add_truthtable_integer_form(i_truthtable)
        
        #check
        if list(self.show_orderedname_regulators_truthtable()) != list(l_order):
            print("Warning! in 'get_truthtable_integer_form_from_logic_equation' method, regulator order has some problem")
    
    def show_regulator_nodes(self):
        l_nodes_regulator = [link.show_start_node() for link in self.l_inwardlinks]
        return l_nodes_regulator
    
    def show_regulator_nodenames(self):
        ls_nodenames = [str(node) for node in self.show_regulator_nodes()]
        return ls_nodenames
    
    def show_regulating_nodes(self):
        l_nodes_regulating = [link.show_end_node() for link in self.l_outwardlinks]
        return l_nodes_regulating
    
    def show_regulating_nodenames(self):
        ls_nodenames = [str(node) for node in self.show_regulating_nodes()]
        return ls_nodenames
    
    def show_connected_links(self):
        return list(set(self.l_inwardlinks+ self.l_outwardlinks))
    
    def show_outwardlinks(self):
        return self.l_outwardlinks
    
    def show_inwardlinks(self):
        return self.l_inwardlinks
    
    def mark_input_node(self):
        self.Bool_inputnode = True
    
    def cancel_input_node(self):
        self.Bool_inputnode = False
    
    def is_input_node(self):
        return self.Bool_inputnode
    
    def mark_output_node(self):
        self.Bool_outputnode = True
        
    def cancel_output_node(self):
        self.Bool_outputnode = False

    def is_output_node(self):
        return self.Bool_outputnode
    
    def is_source_node(self):
        if self.l_inwardlinks:
            return False
        else:
            return True
        
    def is_sink_node(self):
        if self.l_outwardlinks:
            return False
        else:
            return True
        
class Expanded_node(Node):
    def __init__(self, s_name):
        Node.__init__(self, s_name)
        self.s_nodename_original = None
        self.b_on = None
        #attributes for single node
        
        self.b_composite_node = None
        self.l_s_expandednode_component = None
        #attributes for composite node
        
        self.s_suffix_of_on_node = None
        self.s_suffix_of_off_node = None
        self.s_andnode_connector = None
        
    def _set_suffix_connector(self, network_expanded):
        self.s_suffix_of_on_node = network_expanded.show_suffix_on()
        self.s_suffix_of_off_node = network_expanded.show_suffix_off()
        self.s_andnode_connector = network_expanded.show_andnode_connector()
        
        if self.s_andnode_connector in self.s_name:#composite node
            self.b_composite_node = True
            self.l_s_expandednode_component = self.s_name.split(self.s_andnode_connector)
        else:#single node
            self.b_composite_node = False
            if self.s_name[-len(self.s_suffix_of_on_node):] == self.s_suffix_of_on_node:
                self.b_on = True
                self.s_nodename_original = self.s_name[:-len(self.s_suffix_of_on_node)]
            elif self.s_name[-len(self.s_suffix_of_off_node):] == self.s_suffix_of_off_node:
                self.b_on = False
                self.s_nodename_original = self.s_name[:-len(self.s_suffix_of_off_node)]
            else:
                raise ValueError(self.s_name+" is wrong suffix or composite node connector!")
    
    def show_original_name(self):
        return self.s_nodename_original
    
    def is_composite_node(self):
        return self.b_composite_node
    
    def show_name_complementary(self):
        if self.b_composite_node:
            return None
        else:
            if self.b_on:
                return self.s_nodename_original+self.s_suffix_of_off_node
            else:
                return self.s_nodename_original+self.s_suffix_of_on_node
            
    def show_list_of_elements_in_composite(self):
        if self.is_composite_node():
            return self.l_s_expandednode_component
        else:
            raise ValueError(str(self)+" is not composite node but 'show_list_of_elements_in_composite' is called!")
            
    def is_on_state_node(self):
        if self.is_composite_node():
            raise ValueError(str(self)+" is composite node but 'is_on_state_node' method is called!")
        else:
            return self.b_on