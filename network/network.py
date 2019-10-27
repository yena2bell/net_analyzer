# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:14:06 2019

@author: jwKim
"""
import os
import pickle

print(__name__)
from .node import Node, Expanded_node
from .link import Directed_link
from ..dynamics import expanded_network, Boolean_simulation
from ..topology_analysis import feedback_analysis, basic_topology_functions,SCC_analysis, FVS_analysis, MDS_analysis
from ..support_functions import folder_functions
from . import network_generation


class Network_model:
    def __init__(self,s_netname):
        self.s_netname = s_netname
        self.l_nodes = [] #list of Nodes objects
        self.l_links = [] #list of Links objects
        
        self.l_sourcenodes = []#it is not input node. input node should be marked.
        self.l_sinknodes = []
        
        self.s_address_net_folder = "Not yet maden"
        
    def __repr__(self):
        return self.s_netname
    
    def read_network_structure(self, s_network_structure):
        pass
    
    def add_nodes_edges_from_list_form(self, ls_nodenames, lt_edges):
        for s_node in ls_nodenames:
            self.add_node(s_node)
        for t_edge in lt_edges:
            self.add_directed_link(t_edge[0],t_edge[-1])
    
    def add_nodes_edges_random_scale_free_connected(self, i_node_num, i_parameter=2):
        while True:
            ls_nodes, lt_edges = network_generation.gen_network_scale_free_out(i_node_num, i_parameter)
            if len(basic_topology_functions.show_connected_components(ls_nodes, lt_edges)) ==1:#connected network
                break
        self.add_nodes_edges_from_list_form(ls_nodes, lt_edges)
        
    def add_modalities_to_links_randomly(self, f_prob_activation=0.5):
        dic_edge_symbol = network_generation.gen_modalities_to_network(self.l_links,f_prob_activation)
        for link in self.l_links:
            link.change_modality(dic_edge_symbol[link])
    
    def add_Boolean_logic_randomly(self, b_consider_modality=True):
        if b_consider_modality:
            for node in self.l_nodes:
                l_ordered_regulators = node.show_regulator_nodenames()
                dic_predecessor_b_modality = {str(link_inward.show_start_node()):link_inward.is_activating_link() for link_inward in node.show_inwardlinks()}
                i_truthtable = network_generation.get_random_Boolean_logic_table_node(l_ordered_regulators, dic_predecessor_b_modality)
                node.add_truthtable_integer_form(i_truthtable)
        else:
            for node in self.l_nodes:
                l_ordered_regulators = node.show_regulator_nodenames()
                i_truthtable = network_generation.get_random_Boolean_logic_table_node(l_ordered_regulators)
                node.add_truthtable_integer_form(i_truthtable)
    
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
    
    def show_source_nodes(self):
        return self.l_sourcenodes
    
    def show_sink_nodes(self):
        return self.l_sinknodes
    
    def show_nodes_without_Boolean_truthtable(self):
        print("source nodes without Boolean truthtable integer form")
        for node in self.l_sourcenodes:
            if node.show_integerform_of_Boolean_truthtable() == None:
                print(str(node))
        print("node with inward links without Boolean truthtable integer form")
        for node in self.l_nodes:
            if (node not in self.l_sourcenodes) and (node.show_integerform_of_Boolean_truthtable() == None):
                if node.is_input_node():
                    print(str(node)," marked as input node")
                else:
                    print(str(node))
                    
    def show_links(self):
        return self.l_links
    
    def show_address_of_network_folder(self):
        return self.s_address_net_folder
    
    def show_dynamics_information(self):
        dic_nodename_t_truthtable_nodeorder = {}
        for node in self.show_node():
            t_truthtable_nodeorder = (node.show_integerform_of_Boolean_truthtable(), node.show_orderedname_regulators_truthtable())
            dic_nodename_t_truthtable_nodeorder[str(node)] = t_truthtable_nodeorder
        
        return dic_nodename_t_truthtable_nodeorder
            
    
    def show_SCC_decomposition(self):
        ll_SCC = SCC_analysis.decompose_SCC(self.show_nodenames(), self.show_links_list_of_tuple())
        lt_SCC_hierarchy = SCC_analysis.net_of_SCCs(ll_SCC, self.show_links_list_of_tuple())
        dic_code_lSCC = dict(zip(range(len(ll_SCC)),ll_SCC))
        return dic_code_lSCC, lt_SCC_hierarchy
    
    def make_network_folder(self, s_address):
        """make new folder named self.s_netname in the s_address folder"""
        self.s_address_net_folder = os.path.join(s_address,self.s_netname)
        folder_functions.directory_making(self.s_address_net_folder)
    
    def show_links_list_of_tuple(self, b_modality_shown=False):
        """return list of tuple such that (start node name, end node name)
        if b_modality_shown == False, (start node name, end node name)
        if b_modality_shown == True, (start node name, modality, end node name)
        modality == True means activating"""
        if b_modality_shown:
            return [(str(link.show_start_node()),link.is_activating_link(),str(link.show_end_node())) for link in self.l_links]
        else:
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
            
    def select_links_with_selected_start_end(self, s_nodename_start, s_nodename_end):
        l_links_with_selected_start_end = []
        for link in self.show_links():
            if str(link.show_start_node()) == s_nodename_start:
                if str(link.show_end_node()) == s_nodename_end:
                    l_links_with_selected_start_end.append(link)
        
        return l_links_with_selected_start_end        
    
    def add_directed_link(self, s_nodename_start, s_nodename_end, modality=None):
        """modality is True->activation link, False-> inhibitory link"""
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
        
        if not(modality==None):
            if modality:
                directed_link_new.change_modality(True)
            else:
                directed_link_new.change_modality(False)
            
        
    def make_expanded_network(self):#not yet completed
        networkmodel_expanded = Expanded_network("expanded_network_of_"+str(self))
        expanded_network.make_expanded_network_using_Boolean_truthtable(self, networkmodel_expanded)
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


    def find_MDS(self, i_covering_distance=1):
        """find minimum dominating set. i_covering_distance is the distance one MDS node can cover
        return list of MDS nodes list.
        every node of network are either MDS node or downstream node of some MDS node within distance i_covering_distance"""
        return MDS_analysis.find_MDS_directednet_reversely(self.show_nodenames(), self.show_links_list_of_tuple(False), i_covering_distance)
    
    def find_DS(self, i_covereing_distance=1):
        return MDS_analysis.find_DS_directednet(self.show_nodenames(), self.show_links_list_of_tuple(False), i_covereing_distance)
        
        
    
    def get_basin_attractor_under_perturbation_Boolean_synchronous_update(self, dic_perturbednode_state={}):
        """lt_s_node_i_perturbatopm == [(s_nodename, i_perturbed_states), , ,]
        before doing this function, define input nodes"""
 
        dic_i_inputcondition_l_basin = Boolean_simulation.attractor_basin_calculation_for_specific_perturbation(self,
                                                                                                                dic_perturbednode_state)
        return dic_i_inputcondition_l_basin
    
    def get_basin_attractor_under_perturbation_specific_input_Boolean_synchronous_update(self, dic_input_state, dic_perturbednode_state={}):
        l_basins = Boolean_simulation.attractor_basin_calculation_for_specific_inputcondition_perturbation(self,
                                                                                                           dic_input_state,
                                                                                                           dic_perturbednode_state)
        return l_basins
    
    def get_attractor_under_perturbation_specific_input_Boolean_synchronous_update(self,
                                                                                   dic_input_state, 
                                                                                   dic_perturbednode_state={},
                                                                                   l_initial_state=None,
                                                                                   i_initial_random_seed=None):
        l_array_attractor = Boolean_simulation.attractor_calculation_for_specific_inputcondition_perturbation(self,
                                                                                                            dic_input_state,
                                                                                                            dic_perturbednode_state,
                                                                                                            l_initial_state,
                                                                                                            i_initial_random_seed)
        return l_array_attractor
    
    def get_attractors_from_random_initial_iteratively(self,
                                                       dic_input_state,
                                                       dic_perturbed_state={}, 
                                                       i_maximum_interval_without_new_att=10000, 
                                                       i_maximum_calculation=None,
                                                       i_random_seed=None):

        l_attractors, li_count_found = Boolean_simulation.attractors_calculation_from_ramdom_initial_states_iteratively(self,
                                                                                                                        dic_input_state,
                                                                                                                        dic_perturbed_state,
                                                                                                                        i_maximum_interval_without_new_att,
                                                                                                                        i_maximum_calculation,
                                                                                                                        i_random_seed)
        #need some code. 
        #using li_count_found, show graph of attractor discovery fequency
        return l_attractors
    
    def find_FVS(self):
        ll_FVS = FVS_analysis.FVS_finding(self.show_nodenames(), self.show_links_list_of_tuple())
        return ll_FVS
    
    def save_using_pickle(self):
        s_name_save = "pickle_save_"+str(self)+".bin"
        with open(os.path.join(self.show_address_of_network_folder(),s_name_save), 'wb') as file_pickle:
            pickle.dump(self, file_pickle)
            
    def find_all_feedbacks(self):
        ll_feedbacks = feedback_analysis.find_all_feedback(self.show_nodenames(), self.show_links_list_of_tuple(False))
        return ll_feedbacks
    
    def find_feedback_cutting_nodes(self):
        l_FCNs = FVS_analysis.find_feedback_cutting_nodes(self.show_nodenames(), self.show_links_list_of_tuple())
        return l_FCNs
        
        


class Expanded_network(Network_model):
    def __init__(self, s_netname):
        Network_model.__init__(self, s_netname)
        self.s_suffix_of_on_node = "_1"
        self.s_suffix_of_off_node = "_0" #if s_suffix_of_on_node[-len(s_suffix_of_off_node):] == s_suffix_of_off_node then occurs bug. vice versa
        self.s_andnode_connector = "__AND__"
        
        self.l_nodes_single = []
        self.l_nodes_composite = []
        
    def find_stable_motifs_using_expanded_net(self):
        ll_stable_motifs = expanded_network.find_stable_motifs_using_expanded_net(self)
        
        return ll_stable_motifs
    
    def show_suffix_on(self):
        return self.s_suffix_of_on_node
    
    def show_suffix_off(self):
        return self.s_suffix_of_off_node
    
    def show_andnode_connector(self):
        return self.s_andnode_connector
    
    def add_node(self, s_node_name):
        """add new node to the network.
        if there exist a node with same name,
        raise error"""
        l_s_nodenames = self.show_nodenames()
        if s_node_name in l_s_nodenames:
            print("node having same name already exists!")
            print("no change to the model")
            return
        node_new = Expanded_node(s_node_name)
        node_new._set_suffix_connector(self)
        self.l_nodes.append(node_new)
        self.l_sourcenodes.append(node_new)
        self.l_sinknodes.append(node_new)
        #same as Network_model.add_node(s_node_name) except Node->Expanded_node
        
        if node_new.is_composite_node():#composite node
            self.l_nodes_composite.append(node_new)
        else:
            self.l_nodes_single.append(node_new)
            
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
        #same to Network_model.delete_node(s_node_name)
        
        if node_to_delete.is_composite_node():#composite node
            i_position = [str(node) for node in self.l_nodes_composite].index(str(node_to_delete))
            self.l_nodes_composite.pop(i_position)
        else:
            i_position = [str(node) for node in self.l_nodes_single].index(str(node_to_delete))
            self.l_nodes_single.pop(i_position)
        
    def show_single_nodes(self):
        return self.l_nodes_single
    
    def show_composite_nodes(self):
        return self.l_nodes_composite
    
    def make_subnetwork(self, l_nodes_subnetwork):
        lt_links_sub = basic_topology_functions.extract_subnet_topology(self.show_links_list_of_tuple(), l_nodes_subnetwork)
        net_sub = Expanded_network("subnet_of_"+str(self))
        net_sub.add_nodes_edges_from_list_form(l_nodes_subnetwork, lt_links_sub)

        return net_sub