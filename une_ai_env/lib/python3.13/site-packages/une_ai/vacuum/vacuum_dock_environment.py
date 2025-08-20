from une_ai.vacuum import VacuumEnvironment

class VacuumDockEnvironment(VacuumEnvironment):

    def __init__(self, w, h):
        super().__init__(w, h)

        self._dock_location = self._agent_state['position']
        self._max_battery_level = 300
    
    def get_charging_dock_location(self):
        return self._dock_location
    
    def get_percepts(self):
        percepts = super().get_percepts()
        percepts['charging-dock-location-sensor'] = self.get_charging_dock_location()

        return percepts
    
    def recharge(self):
        self._agent_state['battery'] = self._max_battery_level
    
    def state_transition(self, agent_actuators):
        agent_state = self.get_agent_state()
        agent_pos = agent_state['position']
        if agent_pos == self.get_charging_dock_location():
            self.recharge()
        return super().state_transition(agent_actuators)
    
    