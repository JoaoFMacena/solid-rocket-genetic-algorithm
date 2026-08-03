gas_constant = 8314.462618

class SolidMotor:
    def __init__(self, diameter, length, mass, propellant_grain, nozzle):
        self.internal_diameter = diameter
        self.length = length
        self.mass = mass
        self.propellant_grain = propellant_grain
        self.nozzle = nozzle

    def get_chamber_mass(self):
        generated_mass = self.propellant_grain.get_burn_area() * self.propellant_grain.get_regression_rate(self.chamber_pressure) * self.propellant_grain.grain_density
        exit_mass = self.nozzle.get_exit_mass()
        stocked_gas_mass = generated_mass - exit_mass
        return stocked_gas_mass

    def get_chamber_free_volume(self):
        chamber_free_volume = self.propellant_grain.get_port_area() * self.length 
        return chamber_free_volume

    def get_pressure_by_density(self, chamber_gas_density, atmospheric_pressure):
        stagnation_temperature = self.propellant_grain.get_propellant_data('stagnation_temperature')
        specific_gas_constant = self.propellant_grain.get_propellant_data('specific_gas_constant')
        chamber_pressure = chamber_gas_density * gas_constant * stagnation_temperature
        return chamber_pressure + atmospheric_pressure

    def get_pressure_by_kn(self, burn_area, throat_area, atmospheric_pressure):
        stagnation_temperature = self.propellant_grain.propellant.get_propellant_data('stagnation_temperature')
        specific_gas_constant = self.propellant_grain.propellant.get_propellant_data('specific_gas_constant')
        gamma_chamber = self.propellant_grain.propellant.get_propellant_data('gamma_chamber')

        kn = burn_area / throat_area
        chamber_pressure = (kn ** (gamma_chamber / (gamma_chamber - 1))) * (stagnation_temperature / specific_gas_constant)
        return chamber_pressure + atmospheric_pressure