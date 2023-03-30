from bppy.model.event_selection.simple_event_selection_strategy import SimpleEventSelectionStrategy
from bppy import BEvent
import graphviz


class Node:
    def __init__(self, prefix, data):
        self.prefix = prefix
        self.data = data
        self.transitions = {}
        if data is None:
            self.must_finish = False
        else:
            self.must_finish = data.get('must_finish', False)

    def __key(self):
        return str(self.data)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __str__(self):
        return str(self.prefix) + str(self.data)


class DFSBThread:
    def __init__(self, bthread_gen, ess, event_list):
        self.bthread_gen = bthread_gen
        self.ess = ess
        self.event_list = event_list

    def get_state(self, prefix):
        bt = self.bthread_gen()
        s = bt.send(None)
        for e in prefix:
            if s is None:
                break
            if 'block' in s:
                if isinstance(s.get('block'), BEvent):
                    if BEvent(e) == s.get('block'):
                        return None
                else:
                    if BEvent(e) in s.get('block'):
                        return None
            if self.ess.is_satisfied(BEvent(e), s):
                s = bt.send(e)
        if s is None:
            return {}
        return s

    def run(self):
        init_s = Node(tuple(), self.get_state(tuple()))
        visited = set()
        stack = []
        stack.append(init_s)

        while len(stack):
            s = stack.pop()
            if s not in visited:
                visited.add(s)

            for e in self.event_list:
                new_s = Node(s.prefix + (e,), self.get_state(s.prefix + (e,)))
                if new_s.data is None:
                    continue
                s.transitions[e] = new_s
                if new_s not in visited:
                    stack.append(new_s)
        return init_s, visited

    @staticmethod
    def save_graph(init, states, name):
        g = graphviz.Digraph()
        map = {}
        for i, s in enumerate(states):
            g.node(str(i), shape='doublecircle' if s == init else 'circle')
            map[s] = str(i)
        for s in states:
            for e, s_new in s.transitions.items():
                g.edge(map[s], map[s_new], label=e)
        g.save(name)
        return g


if __name__ == "__main__":
    from hot_cold import *
    def gen():
        return control()
    event_list = ["Start", "HOT", "COLD", "IDLE"]
    dfs = DFSBThread(gen, SimpleEventSelectionStrategy(), event_list)
    init_s, visited = dfs.run()
    DFSBThread.save_graph(init_s, visited, "dfs.dot")

