import time
import math
import matplotlib.pyplot as plt
from ADS1256 import ADS1256

### === Vacuum Sensor === ###

class PfeifferVacuumSensor:
    def __init__(self, adc, channel=0):
        self.adc = adc
        self.channel = channel
        self.vref = 5.0      # Reference voltage for ADC
        self.a = 1.667       # Calibration slope (sensor-specific)
        self.d = 11.33       # Calibration offset (sensor-specific)

    def read_raw(self):
        return self.adc.ADS1256_GetChannalValue(self.channel)

    def raw_to_voltage(self, raw):
        # Convert raw 24-bit signed ADC value to voltage
        if raw & 0x800000:
            raw -= 1 << 24
        return (raw / float(0x7FFFFF)) * self.vref

    def voltage_to_pressure(self, voltage):
        # Calculate pressure in mbar, then convert to bar
        pressure_mbar = 10 ** (self.a * voltage - self.d)
        return pressure_mbar / 1000  # Convert to bar

    def run(self):
        voltages = []
        pressures = []

        print("\nReading Vacuum Sensor... Press Ctrl+C to stop.\n")
        try:
            while True:
                raw = self.read_raw()
                voltage = self.raw_to_voltage(raw)
                pressure_bar = self.voltage_to_pressure(voltage)
                print(f"Voltage: {voltage:.3f} V | Pressure: {pressure_bar:.3e} bar")
                voltages.append(voltage)
                pressures.append(pressure_bar)
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nMeasurement stopped. Plotting results...\n")
            plt.plot(voltages, pressures, 'o-', color='blue')
            plt.yscale('log')
            plt.title("Vacuum Pressure vs Voltage")
            plt.xlabel("Voltage (V)")
            plt.ylabel("Pressure (bar)")
            plt.grid(True, which='both')
            plt.tight_layout()
            plt.show()
