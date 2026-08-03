import math

class Nozzle:
    def __init__(self, throat_diameter, exit_diameter):
        self.throat_diameter = throat_diameter
        self.exit_diameter = exit_diameter
        self.throat_area = (throat_diameter / 2) ** 2 * math.pi
        self.exit_area = (exit_diameter / 2) ** 2 * math.pi
        self.expansion_ratio = self.exit_area / self.throat_area

    def _resolve_propellant(self, propellant):
        if propellant is None:
            return None
        if hasattr(propellant, 'get_propellant_data'):
            return propellant
        grain_propellant = getattr(propellant, 'propellant', None)
        if grain_propellant is not None and hasattr(grain_propellant, 'get_propellant_data'):
            return grain_propellant
        return None

    def get_mass_flow(self, chamber_pressure, propellant):
        """Estimate choked mass flow at the throat using isentropic choked-flow relation.

        chamber_pressure: stagnation pressure (Pa)
        propellant: object exposing get_propellant_data() -> dict with keys:
          - 'gamma_nozzle' or 'gamma_chamber'
          - 'specific_gas_constant'
          - 'stagnation_temperature'
        """
        resolved_propellant = self._resolve_propellant(propellant)
        if resolved_propellant is None:
            return 0.0

        data = resolved_propellant.get_propellant_data()
        gamma = data.get('gamma_nozzle', data.get('gamma_chamber', 1.4))
        R = data.get('specific_gas_constant', 287.0)
        T0 = data.get('stagnation_temperature', 300.0)

        At = self.throat_area
        # choked mass flow per unit area: p0 / sqrt(T0) * sqrt(gamma/R) * factor
        factor = (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1)))
        mdot = chamber_pressure * At * math.sqrt(gamma / (R * T0)) * factor
        return mdot

    def _area_mach_ratio(self, M, gamma):
        return (1.0 / M) * ((2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * M * M)) ** (
            (gamma + 1.0) / (2.0 * (gamma - 1.0))
        )

    def _mach_from_area_ratio(self, area_ratio, gamma):
        """Solve A/A* = f(M) for M (supersonic branch) using bisection."""
        if area_ratio <= 1.0:
            return 1.0

        low = 1.0
        high = 50.0

        for _ in range(100):
            mid = 0.5 * (low + high)
            val = self._area_mach_ratio(mid, gamma)
            
            # Correção da lógica de busca supersônica:
            if val > area_ratio:
                high = mid  # val é maior que o alvo -> o Mach verdadeiro é menor que mid
            else:
                low = mid   # val é menor que o alvo -> o Mach verdadeiro é maior que mid

        return 0.5 * (low + high)

    def get_exhaust_velocity(self, chamber_pressure, propellant, atmospheric_pressure=None):
        """Return exit velocity (m/s) and exit pressure (Pa) for the nozzle given stagnation conditions."""
        resolved_propellant = self._resolve_propellant(propellant)
        if resolved_propellant is None:
            return 0.0, 0.0, 1.0

        data = resolved_propellant.get_propellant_data()
        gamma = data.get('gamma_nozzle', data.get('gamma_chamber', 1.4))
        R = data.get('specific_gas_constant', 287.0)
        T0 = data.get('stagnation_temperature', 300.0)

        Me = self._mach_from_area_ratio(self.expansion_ratio, gamma)
        # static temperature at exit
        Te = T0 / (1.0 + (gamma - 1.0) / 2.0 * Me * Me)
        # exit velocity
        ve = Me * math.sqrt(gamma * R * Te)
        # exit (static) pressure using isentropic relation
        pe = chamber_pressure * (1.0 + (gamma - 1.0) / 2.0 * Me * Me) ** (-gamma / (gamma - 1.0))
        return ve, pe, Me

    def get_thrust(self, chamber_pressure, p_amb, mdot, Ae, At, gamma, R_spec, Tc):
        if chamber_pressure <= p_amb:
            return 0.0

        area_ratio = Ae / At
        Me = self._mach_from_area_ratio(area_ratio, gamma)

        pe = chamber_pressure * (1.0 + (gamma - 1.0) / 2.0 * Me * Me) ** (-gamma / (gamma - 1.0))

        pe_limit = 0.4 * p_amb
        if pe < pe_limit:
            pe = pe_limit

        pr_ratio = pe / chamber_pressure
        ve = (2.0 * gamma / (gamma - 1.0) * R_spec * Tc * (1.0 - pr_ratio ** ((gamma - 1.0) / gamma))) ** 0.5

        thrust = (mdot * ve) + (pe - p_amb) * Ae

        return max(0.0, thrust)
    
    def get_exit_mass(self, chamber_pressure=None, propellant=None, time_step=1.0):
        """Return mass exiting the nozzle over `time_step` seconds.
        If chamber_pressure or propellant are not provided, returns 0.
        """
        if chamber_pressure is None or propellant is None:
            return 0
        mdot = self.get_mass_flow(chamber_pressure, propellant)
        return mdot * time_step

    def get_temperature_at_section(self, point_coordinate):
        # Placeholder for temperature calculation at a specific point in the nozzle
        return 0

    def get_pressure_at_section(self, point_coordinate):
        # Placeholder for pressure calculation at a specific point in the nozzle
        return 0