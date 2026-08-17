import time
import math
import matplotlib.pyplot as plt
from ADS1256 import ADS1256

### === Piezoresistive Pressure Sensor === ###

class PiezoresistivePressureSensor:
    def __init__(self, adc, channel=0, resistor=220, current_range=(4.0, 20.0), pressure_max=7.0):
        self.adc = adc
        self.channel = channel
        self.vref = 5.0
        self.resistor = resistor
        self.current_min, self.current_max = current_range
        self.pressure_max = pressure_max

    def read_raw(self):
        return self.adc.ADS1256_GetChannalValue(self.channel)

    def raw_to_voltage(self, raw):
        if raw & 0x800000:
            raw -= 1 << 24
        return (raw / float(0x7FFFFF)) * self.vref

    def voltage_to_current(self, voltage):
        return (voltage / self.resistor) * 1000

    def current_to_pressure(self, current):
        # current is expected already clamped here
        return ((current - self.current_min) / (self.current_max - self.current_min)) * self.pressure_max

    def run(self):
        print("Pressure Sensor Current Range:")
        print("  1. 4–10 mA\n  2. 8–14 mA\n  3. 14–20 mA")
        choice = input("Choose range: ").strip()
        ranges = [(4.0, 10.0), (8.0, 14.0), (14.0, 20.0)]
        self.current_min, self.current_max = ranges[int(choice) - 1]

        pressures, currents = [], []

        print("\nReading Pressure Sensor. Press Ctrl+C to stop...\n")
        try:
            while True:
                raw = self.read_raw()
                voltage = self.raw_to_voltage(raw)
                current_raw = self.voltage_to_current(voltage)

                # Clamp current before calculation and plotting
                current = max(self.current_min, min(current_raw, self.current_max))
                pressure = self.current_to_pressure(current)

                print(f"V: {voltage:.3f} V | I(raw): {current_raw:.2f} mA | I(clamped): {current:.2f} mA | P: {pressure:.3f} bar")

                pressures.append(pressure)
                currents.append(current)  # Use clamped current for x-axis
                time.sleep(0.5)
        except KeyboardInterrupt:
            plt.plot(currents, pressures, 'go-')
            plt.title("Pressure vs Current")
            plt.xlabel("Current (mA)")
            plt.ylabel("Pressure (bar)")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
