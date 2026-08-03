import math

atmospheric_pressure = 101325  # Pa

from engine.grains.bates import BatesGrains
from engine.ballistics.nozzle import Nozzle
from engine.grains.propellants import Nakka_KNSB
from engine.ballistics.ballistics import SolidMotor


def build_motor():
    """Create the propellant, grain, and nozzle used in the simulation."""
    propellant = Nakka_KNSB()
    grain = BatesGrains(
        grain_core=0.04,
        grain_length=0.17,
        grain_outer_diameter=0.1,
        grain_number=1,
        grain_density=1841,
        propellant=propellant,
        inhibited_ends=0
    )
    nozzle = Nozzle(throat_diameter=0.02, exit_diameter=0.040)
    chamber_length = 0.85
    chamber_outer_radius = 0.1 / 2.0  # Raio interno do tubo do motor
    return grain, nozzle, chamber_length, chamber_outer_radius


def get_free_chamber_volume(grain, chamber_length, chamber_outer_radius):
    """Calcula o volume LIVRE da câmara (Volume do tubo - Volume do grão de propelente)."""
    total_chamber_vol = math.pi * (chamber_outer_radius**2) * chamber_length
    
    # Volume ocupado pelo propelente restante
    grain_vol = grain.grain_number * math.pi * (
        (grain.grain_outer_diameter / 2.0)**2 - (grain.grain_core / 2.0)**2
    ) * grain.grain_length
    
    free_vol = total_chamber_vol - grain_vol
    return max(free_vol, 1e-6)


def initial_chamber_state(grain, chamber_volume, ambient_pressure=atmospheric_pressure):
    data = grain.propellant.get_propellant_data()
    R_spec = data['specific_gas_constant']  
    T0 = data['stagnation_temperature']
    stocked_gas_mass = (ambient_pressure * chamber_volume) / (R_spec * T0)
    return ambient_pressure, stocked_gas_mass


def compute_generated_mass(grain, chamber_pressure, time_step):
    burn_area = grain.get_burn_area()
    regression_rate = grain.get_regression_rate(chamber_pressure)
    return burn_area * regression_rate * grain.grain_density * time_step, regression_rate


def compute_chamber_pressure(stocked_gas_mass, chamber_volume, grain):
    data = grain.propellant.get_propellant_data()
    R_spec = data['specific_gas_constant'] 
    T0 = data['stagnation_temperature']
    pressure = (stocked_gas_mass / chamber_volume) * R_spec * T0
    return max(float(pressure), atmospheric_pressure)

def print_step(time, chamber_pressure, mass_flow, thrust):
    print(
        f"t={time:.3f}s | p={chamber_pressure:.2e} Pa | mdot={mass_flow:.8f} kg/s | thrust={thrust:.1f} N"
    )




def run_simulation(max_time=5.0, time_step=0.00001):
    atmospheric_pressure = 101325.0 

    grain, nozzle, chamber_length, chamber_outer_radius = build_motor()

    # Instanciamos o motor para usar na chamada do método
    motor = SolidMotor(
        diameter=chamber_outer_radius * 2,
        length=chamber_length,
        mass=0.0,
        propellant_grain=grain,
        nozzle=nozzle,
    )

    chamber_volume = get_free_chamber_volume(
        grain, chamber_length, chamber_outer_radius
    )
    chamber_pressure, stocked_gas_mass = initial_chamber_state(
        grain, chamber_volume
    )

    time = 0.0
    print_interval = 0.01
    next_print_time = 0.0

    print("Starting simulation from ambient pressure:")
    print_step(time, chamber_pressure, 0.0, 0.0)

    while time < max_time and grain.grain_core < grain.grain_outer_diameter and grain.grain_length > 0.0:
        chamber_volume = get_free_chamber_volume(
            grain, chamber_length, chamber_outer_radius
        )

        generated_mass, regression_rate = compute_generated_mass(
            grain, chamber_pressure, time_step
        )

        exit_mass = nozzle.get_exit_mass(
            chamber_pressure=chamber_pressure,
            propellant=grain.propellant,
            time_step=time_step,
        )

        chamber_pressure_kn = motor.get_pressure_by_kn(
            burn_area=grain.get_burn_area(),
            throat_area=nozzle.throat_area,
            atmospheric_pressure=atmospheric_pressure,
        )

        exit_mass = min(exit_mass, stocked_gas_mass + generated_mass)

        stocked_gas_mass = max(
            stocked_gas_mass + generated_mass - exit_mass, 0.0
        )
        chamber_pressure = compute_chamber_pressure(
            stocked_gas_mass, chamber_volume, grain
        )

        # 5. Desempenho do bocal
        thrust = nozzle.get_thrust(
            chamber_pressure,
            p_amb=atmospheric_pressure,
            mdot=exit_mass / time_step,
            Ae=nozzle.exit_area,
            At=nozzle.throat_area,
            gamma=grain.propellant.get_propellant_data().get(
                "gamma_nozzle",
                grain.propellant.get_propellant_data().get(
                    "gamma_chamber", 1.4
                ),
            ),
            R_spec=grain.propellant.get_propellant_data().get(
                "specific_gas_constant", 200
            ),
            Tc=grain.propellant.get_propellant_data().get(
                "stagnation_temperature", 300.0
            ),
        )
        mass_flow = exit_mass / time_step

        # Print periódico
        if time >= next_print_time:
            # print_step(time, chamber_pressure, mass_flow, thrust)
            next_print_time += print_interval

            # CORREÇÃO: Ajustado o print para exibir o tempo dinâmico t=time
            #print(f"--- DIAGNÓSTICO t={time:.2f}s ---")
            #print(f"Área de Queima (Ab): {grain.get_burn_area():.6f} m²")
            #print(f"Taxa de Regressão (r): {regression_rate * 1000:.2f} mm/s")
            #print(f"Pressão da Câmara (Pc): {chamber_pressure / 1e6:.2f} MPa")
            #print(
            #    f"Pressão por Kn (Pc_Kn): {chamber_pressure_kn / 1e6:.2f} MPa"
            #)
            #print(f"Vazão Mássica (mdot): {mass_flow:.3f} kg/s")
            #print(f"Empuxo (Thrust): {thrust:.1f} N\n")

        grain.regression(time_step, regression_rate)
        time += time_step

    print("Simulation complete.")


if __name__ == "__main__":
    run_simulation()