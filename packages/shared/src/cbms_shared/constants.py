"""Physical and scientific constants."""

# Universal
R_GAS = 8.314  # J/(mol·K)
AVOGADRO = 6.022e23
FARADAY = 96485.0  # C/mol

# Standard conditions
STD_TEMP_K = 273.15 + 25  # 298.15 K
STD_PRESSURE_PA = 101325.0
MOLAR_VOLUME_STP = 22.414e-3  # m³/mol at STP

# Molar masses (g/mol)
MOLAR_MASSES = {
    "CO2": 44.01,
    "SO2": 64.07,
    "NO2": 46.01,
    "NO": 30.01,
    "CaCO3": 100.09,
    "CaSO4": 136.14,
    "CaSO3": 120.14,
    "CaOH2": 74.10,
    "H2O": 18.02,
    "O2": 32.00,
    "N2": 28.01,
}

# Limits
CPCB_SO2_LIMIT_MG_PER_NM3 = 200.0
CPCB_PM_LIMIT_MG_PER_NM3 = 30.0
