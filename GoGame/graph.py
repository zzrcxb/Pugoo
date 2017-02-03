class Graph():
    # Opt option for optimizing speed with more memory needed
    def __init__(self, opt=False):
        self.nodes = {}  # Element is node
        self.arcs = {}  # Elements are a set consisted of nodes
        self.__opt__ = False

    def add_node(self, node, key):
        if not key in self.nodes:
            self.nodes[key] = node
            self.arcs[key] = set()

    def remove_node(self, key):
        if key in self.nodes:
            # Then delete it from nodes and arc
            del self.nodes[key]
            del self.arcs[key]
            for key in self.arcs:
                try:
                    self.arcs[key].remove(key)
                except KeyError:
                    pass

    # Nodes will be combined to the first one, this node for node key
    def combine_nodes(self, nodes):
        if len(nodes) == 1:
            return

        remain = nodes[-1]
        del nodes[-1]

        for node in nodes:
            self.nodes[remain].members = self.nodes[remain].members | self.nodes[node].members
            del self.nodes[node]
            # Combine nodes in arc
            self.arcs[remain] = self.arcs[remain] | self.arcs[node]
            del self.arcs[node]

        for key in self.arcs:
            try:
                for temp_key in nodes:
                    self.arcs[key].remove(temp_key)
            except KeyError:
                pass

    # Be aware of KeyError
    def add_arc(self, key1, key2):
        if key1 != key2:
            self.arcs[key1].add(key2)
            self.arcs[key2].add(key1)

    def get_node(self, key):
        return self.nodes[key]

    def get_arcs(self, key):
            return self.arcs[key]

    def print(self):
        print("Nodes:")
        for key in self.nodes:
            print(self.nodes[key],self.arcs[key], self.nodes[key].life, self.nodes[key].color)
