# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:22:48 2019

@author: jwKim
"""

class Directed_link:
    def __init__(self, Node_start, Node_end):
        self.node_start = Node_start
        self.node_end = Node_end
        
    def __repr__(self):
        return "{}->{}".format(self.node_start, self.node_end)
    
    def show_start_node(self):
        return self.node_start
    
    def show_end_node(self):
        return self.node_end