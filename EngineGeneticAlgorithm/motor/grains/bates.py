import numpy as np

class BatesGrains:
    def __init__(self, grain_core, grain_length, grain_outer_diameter, grain_number, grain_density, inhibited_ends=0):
        self.grain_core = grain_core
        self.grain_length = grain_length
        self.grain_outer_diameter = grain_outer_diameter
        self.grain_density = grain_density
        self.inhibited_ends = inhibited_ends
        self.propellant_data = self.get_propellant_data()


    def get_burn_area(self):
        if self.inhibited_ends == 0: ## Both ends burning
            return (self.grain_core * self.grain_length + (self.grain_outer_diameter**2 - self.grain_core**2)/2) * np.pi
        else: ## Both ends inhibited
            return self.grain_core 

    def get_port_area(self):
        return (self.grain_core / 2) ** 2 * np.pi

    def get_regression_rate(self, chamber_pressure):
        a = self.propellant_data['a']
        n = self.propellant_data['n']
        return a * chamber_pressure ** n

    def regression(self, time_step, regression_rate):
        if self.inhibited_ends == 0:
            core = self.grain_core + regression_rate * time_step
            if core >= self.grain_outer_diameter:
                core = self.grain_outer_diameter

            self.grain_core = core
        else:
            length = self.grain_length - 2 * regression_rate * time_step
            if length <= 0:
                length = 0
            self.grain_length = length

    def get_propellant_data(self):
        # Placeholder for propellant data retrieval
        return {'a': 0.005, 
                'n': 0.3, 
                'stagnation_temperature': 1600,
                'specific_gas_constant': 208.4,
                'gamma_chamber': 1.33,
                'gamma_nozzle': 1.042}
    
    def propellant_mass(self):
        return (self.grain_outer_diameter**2 - self.grain_core**2)/2 * self.grain_length * self.grain_density * np.pi
    
