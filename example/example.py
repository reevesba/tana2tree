import tana2tree as t2t

def main():
    # get tanagra description as input
    input_file = "example/tanagra-output.txt"
    
    # build the tree, returns root node
    tree = t2t.Tanagra_Parser()
    print("Tree: ")
    print(tree.parse(input_file))

    print("\n")

    # list all nodes in tree
    node_list = tree.traverse()
    print("All node attributes and values: ")
    for node in node_list:
        '''
        Possible keys: 
        node.parent: parent attr as string
        node.parent_op: parent operator as string
        node.attr: current attr as string
        node.op: current operator as string
        node.value: current value as float
        '''
        print("Attribute: " + node.attr + ", Value: " + str(node.value))

    print("\n")

    # list specific node
    print("Node 'wc': ")
    node = tree.get_node("wc")
    print(node)

    print("\n")

    # print tree in readable format
    print("Pretty print tree: ")
    tree.print_tree()

    print("\n")

    # return tree as dict
    print("Tree formatted as dict:")
    d = tree.make_dict(unique_values=True)
    print(d)

    print("Tree formatted as dict (original labels):")
    d = tree.make_dict()
    print(d)

if __name__ == '__main__':
    main()