atmospheric_pressure = 101325  # Pa

from engine.grains.bates import BatesGrains
from engine.ballistics.nozzle import Nozzle
from engine.propellants import default_htpb


def build_motor():
    """Create the propellant, grain, and nozzle used in the simulation."""
    propellant = default_htpb()
    grain = BatesGrains(
        grain_core=0.02,
        grain_length=0.1,
        grain_outer_diameter=0.05,
        grain_number=1,
        grain_density=1800,
        propellant=propellant,
    )
    nozzle = Nozzle(throat_diameter=0.02, exit_diameter=0.04)
    chamber_length = 0.15
    chamber_volume = grain.get_port_area() * chamber_length
    return grain, nozzle, chamber_volume


def initial_chamber_state(grain, chamber_volume, ambient_pressure=atmospheric_pressure):
    """Start the chamber at ambient pressure and compute initial gas mass."""
    data = grain.propellant.get_propellant_data()
    R = data['specific_gas_constant']
    T0 = data['stagnation_temperature']
    stocked_gas_mass = (ambient_pressure * chamber_volume) / (R * T0)
    return ambient_pressure, stocked_gas_mass


def compute_generated_mass(grain, chamber_pressure, time_step):
    burn_area = grain.get_burn_area()
    regression_rate = grain.get_regression_rate(chamber_pressure)
    return burn_area * regression_rate * grain.grain_density * time_step, regression_rate


def compute_chamber_pressure(stocked_gas_mass, chamber_volume, grain):
    data = grain.propellant.get_propellant_data()
    R = data['specific_gas_constant']
    T0 = data['stagnation_temperature']
    return (stocked_gas_mass / chamber_volume) * R * T0


def print_step(time, chamber_pressure, mass_flow, thrust):
    print(
        f"t={time:.2f}s | p={chamber_pressure:.2e} Pa | mdot={mass_flow:.2f} kg/s | thrust={thrust:.1f} N"
    )


def run_simulation(max_time=5.0, time_step=0.01):
    grain, nozzle, chamber_volume = build_motor()
    chamber_pressure, stocked_gas_mass = initial_chamber_state(grain, chamber_volume)
    time = 0.0

    print("Starting simulation from ambient pressure:")
    print_step(time, chamber_pressure, 0.0, 0.0)

    while time < max_time and grain.grain_core < grain.grain_outer_diameter:
        generated_mass, regression_rate = compute_generated_mass(
            grain, chamber_pressure, time_step
        )
        exit_mass = nozzle.get_exit_mass(
            chamber_pressure=chamber_pressure, propellant=grain, time_step=time_step
        )
        stocked_gas_mass += generated_mass - exit_mass
        chamber_pressure = compute_chamber_pressure(stocked_gas_mass, chamber_volume, grain)

        thrust = nozzle.get_thrust(chamber_pressure, p_amb=atmospheric_pressure, propellant=grain)
        mass_flow = exit_mass / time_step
        print_step(time + time_step, chamber_pressure, mass_flow, thrust)

        grain.regression(time_step, regression_rate)
        time += time_step

    print("Simulation complete.")


if __name__ == "__main__":
    run_simulation()
