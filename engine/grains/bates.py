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
        inhibited_ends,
    ):
        """Initialize the Bates grain geometry and propellant data.

        Arguments:

        grain_core: float (m)
        - grain_core: Internal port diameter in meters.

        grain_length: float (m)
        - grain_length: Length of a single grain in meters.

        grain_outer_diameter: float (m)
        - grain_outer_diameter: Outer diameter of the grain in meters.

        grain_number: int
        - grain_number: Number of grains in the motor.

        grain_density: float (kg/m³)
        - grain_density: Propellant density in kilograms per cubic meter.

        propellant: object
        - propellant: Propellant object with burn law parameters.

        inhibited_ends: int (0 or 1)
        - inhibited_ends: 0 if ends burn, 1 if ends are inhibited.
        """
        self.grain_core = grain_core
        self.grain_length = grain_length
        self.grain_outer_diameter = grain_outer_diameter
        self.grain_number = grain_number
        self.grain_density = grain_density
        self.inhibited_ends = inhibited_ends
        self.propellant = propellant

    def get_burn_area(self):
        """Return the total burning surface area of all grains.

        Returns:

        float (m²)
        - Total burning surface area in square meters.
        """
        inner_core_area = np.pi * self.grain_core * self.grain_length

        if self.inhibited_ends == 0:
            ends_area = 2.0 * (np.pi / 4.0) * (
                self.grain_outer_diameter**2 - self.grain_core**2
            )
            single_grain_area = inner_core_area + ends_area
        else:
            single_grain_area = inner_core_area

        return single_grain_area * self.grain_number

    def get_port_area(self):
        """Return the cross-sectional port area of the internal grain hole.

        Returns:

        float (m²)
        - Port area in square meters.
        """
        return (np.pi / 4.0) * (self.grain_core**2)

    def get_regression_rate(self, chamber_pressure_pa):
        """Calculate the burn regression rate from chamber pressure.

        Arguments:

        chamber_pressure_pa: float (Pa)
        - chamber_pressure_pa: Pressure in pascals.

        Returns:

        float (m/s)
        - Burn regression rate in meters per second.
        """
        a = self.propellant.get_propellant_data('a')
        n = self.propellant.get_propellant_data('n')

        p_mpa = max(float(chamber_pressure_pa) / 1e6, 0.1)
        r_mms = a * (p_mpa ** n)
        r_ms = r_mms / 1000.0

        return r_ms

    def regression(self, time_step, regression_rate):
        """Update the grain geometry based on burn regression.

        Arguments:

        time_step: float (s)
        - time_step: Time increment in seconds.

        regression_rate: float (m/s)
        - regression_rate: Burn regression rate in meters per second.
        """
        dr = regression_rate * time_step

        self.grain_core += 2.0 * dr
        if self.grain_core >= self.grain_outer_diameter:
            self.grain_core = self.grain_outer_diameter

        if self.inhibited_ends == 0:
            self.grain_length -= 2.0 * dr
            if self.grain_length <= 0:
                self.grain_length = 0.0


    def propellant_mass(self):
        """Return the remaining propellant mass for all grains.

        Returns:

        float (kg)
        - Remaining propellant mass in kilograms.
        """
        volume_single_grain = (np.pi / 4.0) * (
            self.grain_outer_diameter**2 - self.grain_core**2
        ) * self.grain_length

        return volume_single_grain * self.grain_density * self.grain_number