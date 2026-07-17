import numpy as np
import math

from motor/grains import

class Nozzle:
    def __init__(self, throat_diameter, exit_diameter):
        self.throat_diameter = throat_diameter
        self.exit_diameter = exit_diameter
        self.throat_area = (throat_diameter / 2)**2 * np.pi
        self.exit_area = (exit_diameter / 2)**2 * np.pi
        self.expansion_ratio = self.exit_area / self.throat_area

    def get_mass_flow(self, chamber_pressure, propellant):
        return (chamber_pressure * self.throat_area) / propellant.c_star

    def get_thrust(self, chamber_pressure, p_amb, propellant):
        
        pass

    def get_temperature_at_section(self, point_coordinate):
        # Placeholder for temperature calculation at a specific point in the nozzle
        return 0

    def get_pressure_at_section(self, point_coordinate):
        # Placeholder for pressure calculation at a specific point in the nozzle
        return 0  # Example value, replace with actual calculation