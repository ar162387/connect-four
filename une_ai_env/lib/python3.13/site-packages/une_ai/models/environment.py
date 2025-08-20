from abc import ABC, abstractmethod

class Environment(ABC):

    def __init__(self, environment_name):
        self._name = environment_name
    
    def get_environment_name(self):
        return self._name
    
    @abstractmethod
    def get_percepts(self):
        pass

    @abstractmethod
    def state_transition(self, agent_actuators):
        pass