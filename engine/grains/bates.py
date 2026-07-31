import numpy as np

class BatesGrains:
    def __init__(
        self,
        grain_core,
        grain_length,
        grain_outer_diameter,
        grain_number,
        grain_density,
        propellant,
        inhibited_ends=0,
    ):
        self.grain_core = grain_core
        self.grain_length = grain_length
        self.grain_outer_diameter = grain_outer_diameter
        self.grain_number = grain_number
        self.grain_density = grain_density
        self.inhibited_ends = inhibited_ends
        self.propellant = propellant

    def get_burn_area(self):
        if self.inhibited_ends == 0:  # Both ends burning
            return ((self.grain_core * self.grain_length + (self.grain_outer_diameter**2 - self.grain_core**2) / 2) * np.pi) * self.grain_number
        return self.grain_core * self.grain_number

    def get_port_area(self):
        return (self.grain_core / 2) ** 2 * np.pi * self.grain_number

    def get_regression_rate(self, chamber_pressure):
        a  = self.propellant.get_propellant_data('a')
        n = self.propellant.get_propellant_data('n')
        return a * chamber_pressure ** n

    def regression(self, time_step, regression_rate):
        if self.inhibited_ends == 0:
            core = self.grain_core + regression_rate * time_step
            if core >= self.grain_outer_diameter:
                core = self.grain_outer_diameter
            self.grain_core = core
            return

        length = self.grain_length - 2 * regression_rate * time_step
        if length <= 0:
            length = 0
        self.grain_length = length

    def propellant_mass(self):
        return (
            (self.grain_outer_diameter**2 - self.grain_core**2)
            / 2
            * self.grain_length
            * self.grain_density
            * np.pi
        )*self.grain_number
    
