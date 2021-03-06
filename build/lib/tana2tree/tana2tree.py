# Author:   Bradley Reeves <bradleyaaronreeves@gmail.com>
# Date:     October 18, 2020
# About:    Converts a Tanagra tree description from HTML
#           to a usable format.

import tana2tree.tree as t
import time
import re

class Tanagra_Parser:
    def __init__(self):
        ''' Parameters
            ----------
            self: tanagra parser object
            Returns
            -------
            None
        '''
        self.root = None
        self.orig_labels = {}

    def __next_tag(self, s, i):
        ''' Parameters
            ----------
            self: tanagra parser object
            s: string to search
            i: starting index as integer
            Returns
            -------
            next html tag as string 
        '''
        return re.search("</*..>", s[i:])

    def __get_file(self, file_name):
        ''' Parameters
            ----------
            self: tanagra parser object
            file_name: path/name of file as string
            Returns
            -------
            file as string 
        '''
        with open(file_name) as file_in:
            return file_in.read()

    def print_tree(self):
        ''' Parameters
            ----------
            self: tanagra parser object
            Returns
            -------
            None: prints tree to terminal
        '''
        self.root.print_tree()
    
    def set_orig_labels(self, d, u):
        ''' Parameters
            ----------
            self: tanagra parser object
            d: tree as dict with unique labels
            u: dict of labels to update

            Returns
            -------
            tree as dict with original labels
        '''
        for k, v in d.items():
            if type(v) is dict:
                self.set_orig_labels(v, u)
            elif k == "attr":
                d[k] = u[v]
        return d
    
    def make_dict(self, unique_values=False):
        ''' Parameters
            ----------
            self: tanagra parser object

            Returns
            -------
            tree as dict
        '''
        d = self.root.to_dict(self.root.traverse(self.root))
        if unique_values is False:
            d = self.set_orig_labels(d, self.orig_labels)
        return d

    def get_node(self, attr):
        ''' Parameters
            ----------
            self: tanagra parser object
            attr: node to retrieve as string
            Returns
            -------
            node object as list
        '''
        return self.root.get_node(self.root, attr)

    def traverse(self):
        ''' Parameters
            ----------
            self: tanagra parser object
            Returns
            -------
            tree nodes as list
        '''
        return self.root.traverse(self.root)

    def parse(self, input_file):
        ''' Parameters
            ----------
            self: tanagra parser object
            input_file: tanagra description
            Returns
            -------
            root node of tree
        '''
        # initialize variables to be used
        depth, start_index = 0, 0
        end = False

        # dict that stores 
        # parents and their operators
        parents_ops = {}

        # used to store unique keys
        # parent can appear twice, targets
        # can only appear once
        labels = []

        # get Tanagra output
        descr = self.__get_file(input_file)

        # remove noise
        # \(.*?\) is everything between parenthesis
        # <\/?[b]> is bold tags
        descr = re.sub("\(.*?\)|<\/?[b]>", "", descr)

        # extract target column name
        target_header = re.search("<th>Target attribute</th>", descr).end(0)
        target_start_i = target_header + self.__next_tag(descr, target_header).end()
        target_col_name = descr[target_start_i:target_start_i + self.__next_tag(descr, target_start_i).start()][:-1]

        # extract the unordered list
        descr = re.search("<UL>(.*)</UL>", descr).group(0)

        # loop through all tags in UL
        while not end:
            if self.__next_tag(descr, start_index):
                # get the next tag and ending index
                # ending index is used as start index of next search
                tag = self.__next_tag(descr, start_index).group(0)
                start_index = start_index + self.__next_tag(descr, start_index).end()

                if tag == "<UL>":
                    # we go down a tree level
                    # for each <UL> tag
                    depth = depth + 1

                elif tag == "<LI>":
                    # extract the list item string
                    s = descr[start_index:start_index + self.__next_tag(descr, start_index).start()]

                    # create attribute labels
                    # by joining first letter of each word
                    # also getting operator
                    op = ""
                    if s.find("<") != -1:
                        ss = s[:s.find("<")]
                        op = "<"
                    else:
                        ss = s[:s.find(">")]
                        op = ">="

                    if ss.find("_") != -1: attr = ss.split("_")
                    elif ss.find("-") != -1: attr = ss.split("-")
                    elif ss.find(".") != -1: attr = ss.split(".")
                    else: attr = ss.split()

                    # if multiple words, use first character of each word
                    # otherwise, use the first two characters of word
                    if len(attr) > 1: attr = "".join(c[0] for c in attr)
                    else: attr = attr[0][:2]
                    
                    # get the values
                    # [\d]+[.,\d]+ is values w/ commas
                    # [\d]*[.][\d]+ is floating point values
                    # [\d]+ is integers
                    value = float(re.search('[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+', s).group(0))

                    # insert the root node
                    if depth == 1 and op == "<":
                        self.root = t.Tree_Node(None, None, attr, op, value)

                    # parent nodes can have at most
                    # two labels
                    post_fix = 0
                    while labels.count(attr) > 1:
                        post_fix = post_fix + 1
                        if post_fix == 1: attr = attr + "_" + str(post_fix)
                        else: attr = attr[:-1] + str(post_fix)
                    labels.append(attr)
                    post_fix = 0

                    # insert parent nodes
                    if "op" in parents_ops.keys():
                        if parents_ops["op"] == "<":
                            self.root.insert(parents_ops["parent"], parents_ops["op"],  attr, op, value)
                        else:
                            self.root.insert(parents_ops["parent"], parents_ops["op"], attr, op, value)
                    parents_ops = {"parent": attr, "op": op}
                    self.orig_labels[attr] = ss[:-1]

                    # insert terminal nodes
                    if "then" in s:
                        # extract the target value
                        target = s[s.find(target_col_name + " = ") + len(target_col_name + " = "):].replace(" ", "")

                        # store original name
                        orig_t = target
                        
                        # target values should be unique
                        post_fix = 0
                        while target in labels:
                            post_fix = post_fix + 1
                            if post_fix == 1: target = target + "_" + str(post_fix)
                            else: target = target[:-1] + str(post_fix)
                        labels.append(target)
                        post_fix = 0
                        
                        if op == "<":
                            self.root.insert(attr, op, target, None, None)
                        else:
                            self.root.insert(attr, op, target, None, None) 
                        parents_ops = {}
                        self.orig_labels[target] = orig_t         
                else:
                    # </UL> encountered, so
                    # go up a tree level
                    depth = depth - 1
            else:
                # no more tags found
                end = True

        return self.root