# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:45:29 2019

@author: jwKim
"""
import numpy as np

def arraystate_to_int(array_state):
    array_binary_digit = np.array([pow(2,i) for i in range(len(array_state)-1,-1,-1)])
    return sum(array_state*array_binary_digit)

def int_to_arraystate(i_state, i_num_of_nodes):
    s_state = ("{:>0%d}" %i_num_of_nodes).format(bin(i_state)[2:])
    return np.array(list(s_state), dtype=int)

class Integer_form_numberset:
    """if self.i_integer_form_numberset has binary form of 1001101, then this set has number 0,2,3,6
    it can be used set of natural numbers"""
    def __init__(self, i_first_state=0):
        self.i_integer_form_numberset = int(i_first_state)
    
    def has_the_number(self, i_num):
        if (self.i_integer_form_numberset >> int(i_num))%2 == 1:
            return True
        else:
            return False
        
    def __add__(self, i_num):
        i_num = int(i_num)
        if self.has_the_number(i_num):#set already has i_num. so no change
            return Integer_form_numberset(self.i_integer_form_numberset)
        else:
            return Integer_form_numberset(self.i_integer_form_numberset + pow(2,i_num))
            
    def __sub__(self, i_num):
        i_num = int(i_num)
        if self.has_the_number(i_num):#set already has i_num. so delete it
            return Integer_form_numberset(self.i_integer_form_numberset - pow(2,i_num))
        else:
            return Integer_form_numberset(self.i_integer_form_numberset)
            
    def __repr__(self):
        return "integer_form_set: "+str(self.i_integer_form_numberset)
    
    def show_integer_form(self):
        return self.i_integer_form_numberset
    
    def show_list_form(self):
        i_tmp = self.i_integer_form_numberset
        i = 0
        l_set = []
        while i_tmp:
            if (i_tmp%2) == 1:
                l_set.append(i)
            i += 1
            i_tmp = i_tmp >>1
        return l_set

    def as_generator(self):
        i_tmp = self.i_integer_form_numberset
        if i_tmp > 0:
            i = 0
            while i_tmp:
                if (i_tmp%2) == 1:
                    yield i
                i += 1
                i_tmp = i_tmp >>1
        
    
    def show_smallest_element(self):
        i_tmp = self.i_integer_form_numberset
        if i_tmp == 0:#empty set
            return None
        i = 0
        while i_tmp:
            if (i_tmp%2) == 1:
                return i
            i += 1
            i_tmp = i_tmp >>1
    
    def union(self, integer_form_numberset_another, b_update=False):
        if b_update:
            self.i_integer_form_numberset = self.i_integer_form_numberset | integer_form_numberset_another.show_integer_form()
        else:
            return Integer_form_numberset(self.i_integer_form_numberset | integer_form_numberset_another.show_integer_form())
    
    def intersection(self, integer_form_numberset_another, b_update=False):
        if b_update:
            self.i_integer_form_numberset = self.i_integer_form_numberset & integer_form_numberset_another.show_integer_form()
        else:
            return Integer_form_numberset(self.i_integer_form_numberset & integer_form_numberset_another.show_integer_form())
    
    def difference(self, integer_form_numberset_another, b_update=False):
        """element in this set and not in integer_form_numberset_another set."""
        i_XOR = self.i_integer_form_numberset ^ integer_form_numberset_another.show_integer_form()
        if b_update:
            self.i_integer_form_numberset = self.i_integer_form_numberset & i_XOR
        else:
            return Integer_form_numberset(self.i_integer_form_numberset & i_XOR)
