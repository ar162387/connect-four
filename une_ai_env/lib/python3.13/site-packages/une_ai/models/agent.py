import logging
from abc import ABC, abstractmethod

class Agent(ABC):

    def __init__(self, agent_name, agent_program):
        assert callable(agent_program), "The parameter 'agent_program' must be a function: f(Percepts) -> Actions"

        self._agent_name = agent_name
        self._sensors = {}
        self._actuators = {}
        self._actions = {}
        self._agent_program = agent_program

        self.add_all_sensors()
        self.add_all_actuators()
        self.add_all_actions()
    
    def who_am_I(self):
        return self._agent_name
    
    # ABSTRACT methods

    @abstractmethod
    def add_all_sensors(self):
        pass

    @abstractmethod
    def add_all_actuators(self):
        pass

    @abstractmethod
    def add_all_actions(self):
        pass

    # SENSORS methods
    
    def add_sensor(self, sensor_name, initial_value, validation_function):
        assert sensor_name not in self._sensors.keys(), "The sensor '{0}' already exists for this agent.".format(sensor_name)
        assert callable(validation_function), "The parameter validation_function must be callable."
        assert validation_function(initial_value), "The initial_value {0} set for the sensor '{1}' is not a valid value.".format(initial_value, sensor_name)

        self._sensors[sensor_name] = {
            'value': initial_value,
            'validation-function': validation_function
        }
    
    def _update_sensor_value(self, sensor_name, sensor_value):
        assert sensor_name in self._sensors.keys(), "The sensor '{0}' does not exist.".format(sensor_name)
        assert self._sensors[sensor_name]['validation-function'](sensor_value), "The value {0} is not a valid value for the sensor '{1}'".format(sensor_value, sensor_name)

        self._sensors[sensor_name]['value'] = sensor_value
    
    def sense(self, environment):
        percepts = environment.get_percepts()
        for sensor_name, percept in percepts.items():
            try:
                self._update_sensor_value(sensor_name, percept)
            except Exception as err:
                # sensor does not exist or value is invalid
                logging.warning(err)
    
    def read_sensor_value(self, sensor_name):
        assert sensor_name in self._sensors.keys(), "The sensor '{0}' is not a valid sensor's name".format(sensor_name)
        return self._sensors[sensor_name]['value']
    
    def read_sensors(self):
        sensors = {}
        for sensor_name in self._sensors.keys():
            sensors[sensor_name] = self.read_sensor_value(sensor_name)
        
        return sensors
    
    # Agent thinking behaviour methods

    def think(self):
        actions = self._agent_program(self.read_sensors(), self.read_actuators())
        return actions

    # ACTUATORS / ACTIONS methods

    def add_actuator(self, actuator_name, initial_value, validation_function):
        assert actuator_name not in self._actuators.keys(), "The actuator '{0}' already exists for this agent.".format(actuator_name)
        assert callable(validation_function), "The parameter validation_function must be callable."
        assert validation_function(initial_value), "The initial_value {0} set for the actuator '{1}' is not a valid value.".format(initial_value, actuator_name)
        
        self._actuators[actuator_name] = {
            'value': initial_value,
            'validation-function': validation_function
        }
    
    def _update_actuator_value(self, actuator_name, actuator_value):
        assert actuator_name in self._actuators.keys(), "The actuator '{0}' does not exist.".format(actuator_name)
        assert self._actuators[actuator_name]['validation-function'](actuator_value), "The value {0} is not a valid value for the actuator '{1}'".format(actuator_value, actuator_name)

        self._actuators[actuator_name]['value'] = actuator_value
    
    def read_actuator_value(self, actuator_name):
        assert actuator_name in self._actuators.keys(), "The actuator '{0}' is not a valid actuator's name".format(actuator_name)

        return self._actuators[actuator_name]['value']
    
    def read_actuators(self):
        actuators = {}
        for actuator_name in self._actuators.keys():
            actuators[actuator_name] = self.read_actuator_value(actuator_name)
        
        return actuators
    
    def add_action(self, action_name, action_function):
        assert action_name not in self._actions.keys(), "The action '{0}' already exists for this agent.".format(action_name)
        assert callable(action_function), "The parameter action_function must be callable."
        
        self._actions[action_name] = action_function

    def act(self, actions, environment):
        if actions is not None:
            # updates the actuators based on the 
            # chosen actions and given the action_function
            for action in actions:
                if action not in self._actions.keys():
                    raise KeyError("The action '{0}' is not a valid action for this agent.".format(action))
                else:
                    updated_actuators = self._actions[action]()
                    for actuator_name, actuator_value in updated_actuators.items():
                        self._update_actuator_value(actuator_name, actuator_value)
        
        environment.state_transition(self.read_actuators())

        return True

    