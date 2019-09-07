# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:22:48 2019

@author: jwKim
"""

class Directed_link:
    def __init__(self, Node_start, Node_end):
        self.node_start = Node_start
        self.node_end = Node_end
        self.b_modality = None#activation->True inhibition->False
        
    def __repr__(self):
        return "{}->{}".format(self.node_start, self.node_end)
    
    def show_start_node(self):
        return self.node_start
    
    def show_end_node(self):
        return self.node_end
    
    def is_activating_link(self):
        if self.b_modality == None:
            raise ValueError(str(self)+" link's modality is not determined")
        else:
            return self.b_modality
    
    def change_modality(self, b_modality):
        self.b_modality = b_modality