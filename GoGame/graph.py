from copy import deepcopy, copy

class Graph():
    # Opt option for optimizing speed with more memory needed
    def __init__(self, opt=False):
        self.nodes = {}  # Element is node
        self.arcs = {}  # Elements are a set consisted of nodes
        self.arc_num = {}

    def __deepcopy__(self, memodict={}):
        g = Graph()
        g.nodes = {_: deepcopy(self.nodes[_]) for _ in self.nodes}
        g.arcs = {_: set(tuple(self.arcs[_])) for _ in self.arcs}
        g.arc_num = {_: self.arc_num[_] for _ in self.arc_num}
        return g

    def add_node(self, node, key):
        if not key in self.nodes:
            self.nodes[key] = node
            self.arcs[key] = set()
            self.arc_num[key] = {}

    def remove_node(self, key):
        if key in self.nodes:
            # Then delete it from nodes and arc
            del self.nodes[key]
            del self.arcs[key]
            del self.arc_num[key]
            for k in self.arcs:
                try:
                    self.arcs[k].remove(key)
                    self.nodes[k].lines = len(self.arcs[k])
                    if self.nodes[k].border:
                        self.nodes[k].lines += 1
                    if key in self.arc_num[k]:
                        del self.arc_num[k][key]
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
            for key in self.arcs[node]:
                if key in self.arc_num[remain]:
                    self.arc_num[remain][key] += self.arc_num[node][key]
                else:
                    self.arc_num[remain][key] = self.arc_num[node][key]
            del self.arcs[node]
            del self.arc_num[node]

        remove_keys = []
        for key in self.arcs[remain]:
            if key not in self.nodes:
                remove_keys.append(key)

        for key in remove_keys:
            self.arcs[remain].remove(key)
            del self.arc_num[remain][key]

        for key in self.arcs:
            flag = False
            for temp_key in nodes:
                if temp_key in self.arcs[key]:
                    flag = True
                    self.arcs[key].remove(temp_key)
                    del self.arc_num[key][temp_key]
            if flag:
                if key != remain:
                    self.arcs[key].add(remain)
                    self.arc_num[key][remain] = self.arc_num[remain][key]
            self.nodes[key].lines = len(self.arcs[key])

    # Be aware of KeyError
    def add_arc(self, key1, key2):
        if key1 != key2:
            if key2 in self.arcs[key1]:
                self.arc_num[key1][key2] += 1
                self.arc_num[key2][key1] += 1
            else:
                self.arcs[key1].add(key2)
                self.arc_num[key1][key2] = 1
                self.nodes[key1].lines += 1
                self.arcs[key2].add(key1)
                self.arc_num[key2][key1] = 1
                self.nodes[key2].lines += 1

    def group_dfs(self):
        gonna_visit = [key for key in self.nodes]
        big_groups = []
        while len(gonna_visit) > 0:
            _group = []
            start_point = gonna_visit[0]
            self.dfs(start_point, gonna_visit, _group)
            big_groups.append(_group)
        return big_groups

    def dfs(self, point, gonna_visit, _group):
        gonna_visit.remove(point)
        _group.append(point)
        connected = self.arcs[point]
        for next_point in connected:
            if next_point in gonna_visit:
                self.dfs(next_point, gonna_visit, _group)
        return

    def get_node(self, key):
        return self.nodes[key]

    def get_arcs(self, key):
        return self.arcs[key]

    def get_arc_num(self, key1, key2):
        return self.arc_num[key1][key2]

    def print(self):
        print("Nodes:")
        for key in self.nodes:
            node = self.nodes[key]
            print(node.name, self.arcs[key], self.arc_num[key], node.life, node.color, node.border, node.lines)
