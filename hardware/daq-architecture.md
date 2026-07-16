# Data Acquisition System (DAQ) Architecture

## Recommended DAQ Architecture
- **Sensors**: 4-20 mA, Modbus, HART
- **Edge DAQ / PLC**: National Instruments cDAQ-9189 or Siemens S7-1200
- **Edge Gateway**: Raspberry Pi 5 + 4G modem (Data buffering, Time-series DB, MQTT/HTTPS to cloud)
- **Cloud**: CBMS API

## Recommended Hardware
| Component | Part | Cost (₹) |
| :--- | :--- | :--- |
| Edge DAQ | National Instruments cDAQ-9189 (8-slot) | 3,50,000 |
| Analog input modules | NI 9208 (8-ch ±20mA) ×2 | 1,20,000 |
| Thermocouple input | NI 9213 | 45,000 |
| Controller | Siemens S7-1200 CPU 1214C | 85,000 |
| HMI panel (10") | Siemens KTP1200 | 1,20,000 |
| Edge gateway | Raspberry Pi 5 + 4G modem | 60,000 |
| Industrial enclosure (IP65) | Rittal SE 1935 | 45,000 |
| Power supply (24V DC) | Phoenix Contact | 15,000 |
| **TOTAL DAQ** | | **8,40,000** |

*Alternative (budget)*: Use a Siemens LOGO! or Arduino-based DAQ for ₹2,50,000 (less reliable, but works for pilot)

## Sample Rate & Timing Requirements
| Sensor | Min Sample Rate | Max Latency | Why |
| :--- | :--- | :--- | :--- |
| pH | 0.1 Hz (10s) | 30s | Slow chemistry |
| Conductivity | 0.1 Hz | 10s | Slow |
| Temperature | 1 Hz | 1s | Fast transients during heating |
| Dissolved CO₂ | 0.1 Hz | 60s | Membrane response |
| Dissolved SO₂ | 0.1 Hz | 30s | Membrane response |
| Dissolved O₂ | 0.5 Hz | 5s | Equilibration |
| Turbidity | 0.5 Hz | 5s | Precipitation events |
| ORP | 0.5 Hz | 5s | Fast chemistry |
| Gas flow | 10 Hz | 100ms | Flow fluctuations |
| Gas pressure | 10 Hz | 100ms | Pressure transients |
| Gas T | 1 Hz | 1s | Standard |
| CO₂ (NDIR) | 1 Hz | 1s | Real-time capture rate |
| SO₂ (UV) | 0.1 Hz | 30s | Slow but reliable |
| NOₓ (CL) | 0.1 Hz | 60s | Slow but reliable |
| Slurry flow | 10 Hz | 100ms | Pump pulsations |

*Aggregate data rate*: ~50-100 KB/s (low) — easily handled by MQTT.
