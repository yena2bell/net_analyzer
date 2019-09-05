# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:14:06 2019

@author: jwKim
"""
import os

print(__name__)
from .node import Node
from .link import Directed_link
from ..dynamics import expanded_network, Boolean_simulation
from ..topology_analysis import feedback_analysis, basic_topology_functions,SCC_analysis
from ..support_functions import folder_functions
from . import network_generation

class Network_model:
    def __init__(self,s_netname):
        self.s_netname = s_netname
        self.l_nodes = [] #list of Nodes objects
        self.l_links = [] #list of Links objects
        
        self.l_sourcenodes = []
        self.l_sinknodes = []
        
        self.s_address_net_folder = "Not yet maden"
        
    def __repr__(self):
        return self.s_netname
    
    def read_network_structure(self, s_network_structure):
        pass
    
    def save_network_data(self):
        #save data in self.s_address_net_folder
        pass
    
    def add_nodes_edges_from_list_form(self, ls_nodenames, lt_edges):
        for s_node in ls_nodenames:
            self.add_node(s_node)
        for t_edge in lt_edges:
            self.add_directed_link(t_edge[0],t_edge[1])
    
    def add_nodes_edges_random_scale_free_connected(self, i_node_num, i_parameter=2):
        while True:
            ls_nodes, lt_edges = network_generation.gen_network_scale_free_out(i_node_num, i_parameter)
            if len(basic_topology_functions.show_connected_components(ls_nodes, lt_edges)) ==1:#connected network
                break
        self.add_nodes_edges_from_list_form(ls_nodes, lt_edges)
    
    def show_nodenames(self):
        return [str(node) for node in self.l_nodes]
    
    def show_node(self):
        return self.l_nodes
    
    def show_input_nodes(self):
        return [node for node in self.l_nodes if node.is_input_node()]
    
    def show_not_input_nodes(self):
        return [node for node in self.l_nodes if not node.is_input_node()]
    
    def show_output_nodes(self):
        return [node for node in self.l_nodes if node.is_output_node()]
    
    def show_address_of_network_folder(self):
        return self.s_address_net_folder
    
    def show_SCC_decomposition(self):
        ll_SCC = SCC_analysis.decompose_SCC(self.show_nodenames(), self.show_links_list_of_tuple())
        lt_SCC_hierarchy = SCC_analysis.net_of_SCCs(ll_SCC, self.show_links_list_of_tuple())
        dic_code_lSCC = dict(zip(range(len(ll_SCC)),ll_SCC))
        return dic_code_lSCC, lt_SCC_hierarchy
    
    def make_network_folder(self, s_address):
        """make new folder named self.s_netname in the s_address folder"""
        self.s_address_net_folder = os.path.join(s_address,self.s_netname)
        folder_functions.directory_making(self.s_address_net_folder)
    
    def show_links_list_of_tuple(self):
        """return list of tuple such that (start node name, end node name)"""
        return [(str(link.show_start_node()),str(link.show_end_node())) for link in self.l_links]
    
    def add_node(self, s_node_name):
        """add new node to the network.
        if there exist a node with same name,
        raise error"""
        l_s_nodenames = self.show_nodenames()
        if s_node_name in l_s_nodenames:
            print("node having same name already exists!")
            print("no change to the model")
            return
        node_new = Node(s_node_name)
        self.l_nodes.append(node_new)
        self.l_sourcenodes.append(node_new)
        self.l_sinknodes.append(node_new)
    
    def delete_node(self, s_node_name):
        """delete node and connected edges
        delete in l_nodes, l_sourcenodes, l_sinknodes
        delete connected link information from connected other nodes
        and check the connected nodes are sourcenode or sinknode"""
        l_s_nodenames = self.show_nodenames()
        if s_node_name not in l_s_nodenames:
            print("node having same name doesn't exists!")
            print("no change to the model")
            return
        node_to_delete = self.select_node(s_node_name)
        #deletion to connected node objects
        links_connected = list(node_to_delete.show_connected_links())
        for link in links_connected:
            self.l_links.pop(self.l_links.index(link))
            if link.show_end_node() == node_to_delete:
                link.show_start_node().delete_outwardlink(link)
                if not link.show_start_node().show_outwardlinks():
                    self.l_sinknodes.append(link.show_start_node())
            else:
                link.show_end_node().delete_inwardlink(link)
                if not link.show_end_node().show_inwardlinks():
                    self.l_sourcenodes.append(link.show_end_node())
                    
        self.l_nodes.pop(self.l_nodes.index(node_to_delete))
        try: self.l_sourcenodes.pop(self.l_sourcenodes.index(node_to_delete))
        except: pass
        try: self.l_sinknodes.pop(self.l_sinknodes.index(node_to_delete))
        except: pass
        
    def select_node(self, s_nodename):
        """find Node object in this Network_model object using name.
        name is changed to string value"""
        s_nodename = str(s_nodename)#check for certainty
        l_s_nodenames = self.show_nodenames()
        try:
            return self.l_nodes[l_s_nodenames.index(s_nodename)]
        except ValueError:
            print("node having such name doesn't exist")
    
    def add_directed_link(self, s_nodename_start, s_nodename_end):
        node_start = self.select_node(s_nodename_start)
        node_end = self.select_node(s_nodename_end)
        directed_link_new = Directed_link(node_start, node_end)
        self.l_links.append(directed_link_new)
        
        try: self.l_sourcenodes.pop(self.l_sourcenodes.index(node_end))
        except: pass
        try: self.l_sinknodes.pop(self.l_sinknodes.index(node_start))
        except: pass
    
        node_end.add_inwardlink(directed_link_new)
        node_start.add_outwardlink(directed_link_new)
        
    def make_expanded_network(self):#not yet completed
        networkmodel_expanded = expanded_network.make_expanded_network_using_Boolean_truthtable(self)
        if self.s_address_net_folder == "Not yet maden":
            pass
        else:
            networkmodel_expanded.make_network_folder(self.s_address_net_folder)
        return networkmodel_expanded
    
    def make_subnetwork(self, l_nodes_subnetwork):
        lt_links_sub = basic_topology_functions.extract_subnet_topology(self.show_links_list_of_tuple(), l_nodes_subnetwork)
        net_sub = Network_model("subnet_of_"+str(self))
        net_sub.add_nodes_edges_from_list_form(l_nodes_subnetwork, lt_links_sub)
        
        return net_sub
    
    def get_basin_attractor_under_perturbation_Boolean_synchronous_update(self, lt_s_node_i_perturbation=None, b_make_output_in_onefile=False):
        """lt_s_node_i_perturbatopm == [(s_nodename, i_perturbed_states), , ,]
        before doing this function, define input nodes"""
        if not lt_s_node_i_perturbation:
            lt_s_node_i_perturbation = []
            
        if self.show_address_of_network_folder() == "Not yet maden":
            raise ValueError("before doing 'get_basin_attractor_under_perturbation_Boolean_synchronous_update' method, make the folder")
            
        ls_inputnodenames, ls_not_inputnodenames, dic_nodename_i_truthtable, dic_nodename_array_regulatorinfo = Boolean_simulation.extract_dynamics_information_from_network(self)
        Boolean_simulation.basin_calculation_for_specific_perturbation(ls_inputnodenames, 
                                                                       ls_not_inputnodenames, 
                                                                       dic_nodename_i_truthtable, 
                                                                       dic_nodename_array_regulatorinfo, 
                                                                       lt_s_node_i_perturbation, 
                                                                       self.show_address_of_network_folder(), 
                                                                       b_make_output_in_onefile)
        


class Expanded_network(Network_model):
    def find_stable_motifs_using_expanded_net(self):
        l_nodenames = self.show_nodenames()
        lt_links = self.show_links_list_of_tuple()
        ll_stable_motifs = expanded_network.find_stable_motifs_using_expanded_net(l_nodenames, lt_links)
        
        return ll_stable_motifs
            