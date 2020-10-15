# parses Tanagra tree description
# convert to python tree

import tree as t
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

    def __open_log(self):
        ''' Parameters
            ----------
            self: tanagra parser object

            Returns
            -------
            file object for logging 
        '''
        return open("out/tana2tree_log_" + time.strftime("%Y%m%d-%H%M%S") + ".txt", "w+")

    def print_tree(self):
        ''' Parameters
            ----------
            self: tanagra parser object

            Returns
            -------
            None: prints tree to terminal
        '''
        self.root.print_tree()
    
    def make_dict(self):
        ''' Parameters
            ----------
            self: tanagra parser object

            Returns
            -------
            tree as dict
        '''
        return self.root.to_dict(self.root.traverse(self.root))

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

        # extract the unordered list
        descr = re.search("<UL>(.*)</UL>", descr).group(0)

        # remove noise
        # \(.*?\) is everything between parenthesis
        # <\/?[b]> is bold tags
        descr = re.sub("\(.*?\)|<\/?[b]>", "", descr)

        # open file used to log results
        log = self.__open_log()
        log.write("Converting Tanagra tree to Python tree object\n")

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

                    attr = "".join(c[0] for c in ss.split())
                    
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
                        attr = attr + "_" + str(post_fix)
                    labels.append(attr)
                    post_fix = 0

                    # insert parent nodes
                    if "op" in parents_ops.keys():
                        if parents_ops["op"] == "<":
                            log.write("inserting " + attr + " into " + parents_ops["parent"] + " as left child...\n")
                            self.root.insert(parents_ops["parent"], parents_ops["op"],  attr, op, value)
                        else:
                            log.write("inserting " + attr + " into " + parents_ops["parent"] + " as right child...\n")
                            self.root.insert(parents_ops["parent"], parents_ops["op"], attr, op, value)
                    parents_ops = {"parent": attr, "op": op}

                    # insert terminal nodes
                    if "then" in s:
                        # extract the target value
                        target = s[s.find("target = ") + len("target = "):].replace(" ", "")
                        
                        # target values should be unique
                        post_fix = 0
                        while target in labels:
                            post_fix = post_fix + 1
                            target = target + "_" + str(post_fix)
                        labels.append(target)
                        post_fix = 0
                        
                        if op == "<":
                            log.write("inserting " + target + " into " + attr + " as left child...\n")
                            self.root.insert(attr, op, target, None, None)
                        else:
                            log.write("inserting " + target + " into " + attr + " as right child...\n")
                            self.root.insert(attr, op, target, None, None) 
                        parents_ops = {}            
                else:
                    # </UL> encountered, so
                    # go up a tree level
                    depth = depth - 1
            else:
                # no more tags found
                end = True

        log.close()
        return self.root
