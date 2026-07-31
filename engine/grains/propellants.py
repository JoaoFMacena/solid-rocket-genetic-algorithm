class Propellant:
    def __init__(
        self,
        name,
        a,
        n,
        stagnation_temperature,
        specific_gas_constant,
        gamma_chamber,
        gamma_nozzle,
        c_star=None,
    ):
        self.name = name
        self.a = a
        self.n = n
        self.stagnation_temperature = stagnation_temperature
        self.specific_gas_constant = specific_gas_constant
        self.gamma_chamber = gamma_chamber
        self.gamma_nozzle = gamma_nozzle
        self.c_star = c_star

    def get_propellant_data(self, key=None):
        data = {
            'a': self.a,
            'n': self.n,
            'stagnation_temperature': self.stagnation_temperature,
            'specific_gas_constant': self.specific_gas_constant,
            'gamma_chamber': self.gamma_chamber,
            'gamma_nozzle': self.gamma_nozzle,
            'c_star': self.c_star,
        }
        if key is None:
            return data
        return data.get(key)

def default_apcp():
    return Propellant(
        name='APCP',
        a=0.0045,
        n=0.32,
        stagnation_temperature=1650,
        specific_gas_constant=220.0,
        gamma_chamber=1.30,
        gamma_nozzle=1.05,
        c_star=1500,
    )

def Nakka_KNSB():
    # Richard Nakka's KNSB data
    return Propellant(
        name='NakkaKNSB',
        a=0.0048,
        n=0.31,
        stagnation_temperature=1600,
        specific_gas_constant=208.53,
        gamma_chamber=1.32,
        gamma_nozzle=1.042,
        c_star=908.3, 
    )