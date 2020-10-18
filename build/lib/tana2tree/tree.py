# Author:   Bradley Reeves <bradleyaaronreeves@gmail.com>
# Date:     October 18, 2020
# About:    Converts a Tanagra tree description from HTML
#           to a usable format.

# chained dictionary class
# set a dict value given a key list
class Chain_Dict(dict):
    def set_value(self, key_list, value):
        ''' Parameters
            ----------
            self: Chain Dict object
            key_list: list of dict indexes
            value: string to insert at key_list

            Returns
            -------
            None 
        '''
        t = self
        for key in key_list[:-1]:
            t = t.setdefault(key, {})
        t.setdefault(key_list[-1], value)

# tree node class
# parses Tanagra tree
class Tree_Node:
    def __init__(self, parent, parent_op, attr, op, value):
        ''' Parameters
            ----------
            self: Tree Node object
            parent: parent attr as string
            parent_op: parent operator as string
            attr: current attr as string
            op: current operator as string
            value: current value as float

            Returns
            -------
            None 
        '''
        self.l_branch = None
        self.r_branch = None
        self.parent = parent
        self.parent_op = parent_op
        self.attr = attr
        self.op = op
        self.value = value

    # insert a node into the DT
    def insert(self, parent, parent_op, attr, op, value):
        ''' Parameters
            ----------
            self: Tree Node object
            parent: parent attr as string
            parent_op: parent operator as string
            attr: current attr as string
            op: current operator as string
            value: current value as float

            Returns
            -------
            None 
        '''
        if self.attr == parent:
            if parent_op == "<":
                self.l_branch = Tree_Node(parent, parent_op, attr, op, value)
            else:
                self.r_branch = Tree_Node(parent, parent_op, attr, op, value)
        else:
            if self.l_branch:
                self.l_branch.insert(parent, parent_op, attr, op, value)
            if self.r_branch:
                self.r_branch.insert(parent, parent_op, attr, op, value)

    # print the parsed DT
    def print_tree(self, spacing=""):
        ''' Parameters
            ----------
            self: Tree Node object
            spacing: amount of space at beginning of line

            Returns
            -------
            None 
        '''
        if self.value:
            print(spacing + "Is {0} {1} {2}?".format(self.attr, self.op, self.value))
        else:
            print(spacing + "predict {0}".format(self.attr))

        if self.l_branch: 
            print(spacing + "--> True:")
            self.l_branch.print_tree(spacing + "   ")

        if self.r_branch: 
            print(spacing + "--> False:")
            self.r_branch.print_tree(spacing + "   ")

        # returns all nodes in DT
    def traverse(self, root):
        ''' Parameters
            ----------
            self: Tree Node object
            root: root node of tree

            Returns
            -------
            node_list: all nodes in tree as list 
        '''
        node_list = []
        if root:
            node_list.append(root)
            node_list = node_list + self.traverse(root.l_branch)
            node_list = node_list + self.traverse(root.r_branch)
        return node_list

    # return node object from DT
    def get_node(self, root, attr):
        ''' Parameters
            ----------
            self: Tree Node object
            root: root node of tree
            x: target node attr as string

            Returns
            -------
            node: target node object as list
        '''
        node = []
        if root:
            node = self.get_node(root.l_branch, attr)
            if root.attr == attr: node.append(root)
            node = node + self.get_node(root.r_branch, attr)
        return node

     # return the nested dict item
    def __insert_dict(self, node):
        ''' Parameters
            ----------
            self: Tree Node object
            node: node to insert as node

            Returns
            -------
            dict conaining node attr and value
        '''
        return {'attr': node.attr, 'value': node.value}

    # convert DT to dict
    def to_dict(self, node_list):
        ''' Parameters
            ----------
            self: Tree Node object
            node_list: a list of nodes in tree

            Returns
            -------
            cd: tree as dict
        '''
        cd = Chain_Dict()

        for node in node_list:
            key_list = self.__get_path(self, node.attr)
            cd.set_value(key_list, self.__insert_dict(node))

        return cd

    # check if a path exists
    # to given DT node
    def __has_path(self, node, path, x, move): 
        ''' Parameters
            ----------
            self: Tree Node object
            node: current node object
            path: current path as list of strings
            x: attr to search for as string
            move: direction of travel as list of strings

            Returns
            -------
            True: node exists and has path
            False: node does not exist 
        '''
        if not node: return False
        
        if move == "right": path.append("r_child")  
        if move == "left": path.append("l_child")  
        
        if node.attr == x: return True
        
        if self.__has_path(node.l_branch, path, x, 'left') or\
           self.__has_path(node.r_branch, path, x, 'right'):
            return True
     
        path.pop(-1)
        return False
  
    # return path list to DT node
    def __get_path(self, node, x): 
        ''' Parameters
            ----------
            self: Tree Node object
            node: current node object
            x: attr to search for as string

            Returns
            -------
            path: current path as list of strings 
        '''
        path = ['tree_node']
         
        if not self.__has_path(node, path, x, ''): 
            print("No Path") 

        return path