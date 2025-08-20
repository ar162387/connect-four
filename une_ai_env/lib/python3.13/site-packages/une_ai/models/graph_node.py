class GraphNode():

    def __init__(self, state, parent_node, action, cost=0):
        assert parent_node is None or isinstance(parent_node, GraphNode), "The parent_node parameter must be a GraphNode instance or None."
        self._state = state
        self._parent_node = parent_node
        self._action = action
        self._cost = cost
        self._path = None
        self._path_cost = None
    
    def get_parent_node(self):
        return self._parent_node
    
    def get_cost(self):
        return self._cost
    
    def get_state(self):
        return self._state
    
    def get_action(self):
        return self._action
    
    def get_path(self):
        if self._path is not None and self._path_cost is not None:
            return self._path, self._path_cost
        
        parent_node = self.get_parent_node()
        path_cost = self.get_cost()
        action = self.get_action()
        if parent_node is not None:
            path = [self.get_action()]
        else:
            path = []
        if parent_node is not None:
            path_parent, path_cost_parent = parent_node.get_path()
            path_cost += path_cost_parent
            path = path_parent + path

        self._path = path
        self._path_cost = path_cost
        
        return path, path_cost

    
