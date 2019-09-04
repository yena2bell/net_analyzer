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
        
    def __repr__(self):
        return self.s_name
    
    def add_inwardlink(self, link):
        self.l_inwardlinks.append(link)
        
    def add_outwardlink(self, link):
        self.l_outwardlinks.append(link)
        
    def delete_inwardlink(self, link):
        self.l_inwardlinks.pop(self.l_inwardlinks.index(link))
        
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
            return []
    
    def show_integerform_of_Boolean_truthtable(self):
        if self.dynamics_l_l_order_i_truthtable:
            return self.dynamics_l_l_order_i_truthtable[1]
        else:
            return None
    
    def show_regulator_nodes(self):
        l_nodes_regulator = [link.show_start_node() for link in self.l_inwardlinks]
        return l_nodes_regulator
    
    def show_connected_links(self):
        return list(set(self.l_inwardlinks+ self.l_outwardlinks))
    
    def show_outwardlinks(self):
        return self.l_outwardlinks
    
    def show_inwardlinks(self):
        return self.l_inwardlinks
    

            
            
            