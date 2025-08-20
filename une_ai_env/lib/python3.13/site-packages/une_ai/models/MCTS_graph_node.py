from .graph_node import GraphNode

class MCTSGraphNode(GraphNode):

    def __init__(self, state, parent_node, action):
        super().__init__(state, parent_node, action, 1)
        self._number_of_visits = 0
        self._wins = {}
        
        self._successors = {}
    
    def get_successors(self):
        return list(self._successors.values())
    
    def was_action_expanded(self, action):
        return action in self._successors.keys()
    
    def wins(self, player):
        if player in self._wins.keys():
            return self._wins[player]
        else:
            return 0
    
    def n(self):
        return self._number_of_visits
    
    def add_successor(self, successor_state, action):
        if not self.was_action_expanded(action):
            successor = MCTSGraphNode(successor_state, self, action)
            self._successors[action] = successor

        return self._successors[action]
    
    def is_leaf_node(self):
        return self.n() == 0
    
    def backpropagate(self, winner):
        self._number_of_visits += 1.
        if winner in self._wins.keys():
            self._wins[winner] += 1.
        elif winner is not None:
            self._wins[winner] = 0
        parent = self.get_parent_node()
        if parent is not None:
            parent.backpropagate(winner)