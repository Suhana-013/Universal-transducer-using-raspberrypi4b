import time
import math
import matplotlib.pyplot as plt
from ADS1256 import ADS1256

### === PT100 Sensor === ###
class SimulatedPT100:
    def __init__(self, adc, channel=0, mode="linear"):
        self.adc = adc
        self.channel = channel
        self.vref = 5.0           # ADC reference voltage
        self.R0 = 100.0           # Resistance at 0°C for PT100
        self.alpha = 0.00385      # Linear temperature coefficient
        self.I = 0.005            # Constant current (A)
        self.mode = mode          # "linear" or "nonlinear"
        self.A = 3.9083e-3        # Callendar–Van Dusen coefficient A
        self.B = -5.775e-7        # Callendar–Van Dusen coefficient B
        self.C = -4.183e-12       # Callendar–Van Dusen coefficient C (for T < 0°C)

    def read_raw(self):
        return self.adc.ADS1256_GetChannalValue(self.channel)

    def raw_to_voltage(self, raw):
        if raw & 0x800000:
            raw -= 1 << 24
        return (raw / float(0x7FFFFF)) * self.vref

    def resistance_to_temperature(self, R):
        if self.mode == "linear":
            return (R - self.R0) / self.alpha
        elif self.mode == "nonlinear":
            if R >= self.R0:
                try:
                    A, B = self.A, self.B
                    temp = (-A + ((A**2 - 4 * B * (1 - (R / self.R0))) ** 0.5)) / (2 * B)
                except ValueError:
                    print("⚠  Math domain error while calculating temperature. Returning NaN.")
                    temp = float('nan')
            else:
                # Iterative Newton-Raphson method for T < 0°C
                T = -50.0
                for _ in range(10):
                    f = self.R0 * (1 + self.A * T + self.B * T**2 + self.C * (T - 100) * T**3) - R
                    df = self.R0 * (self.A + 2 * self.B * T + self.C * (4 * T**3 - 300 * T**2 + 30000 * T))
                    T = T - f / df
                temp = T
            return temp
        else:
            raise ValueError("Mode must be 'linear' or 'nonlinear'")

    def read_temperature(self):
        raw = self.read_raw()
        voltage = self.raw_to_voltage(raw)
        resistance = voltage / self.I
        temperature = self.resistance_to_temperature(resistance)
        return temperature, resistance, voltage, raw

    def run(self):
        print("PT100 Mode:")
        print("  1. Linear(valid for 100–138 Ω range)\n  2. Non-linear(Callendar-Van Dusen")
        mode = input("Select mode: ").strip()
        self.mode = "linear" if mode == "1" else "nonlinear"

        print("Temperature Range:")
        print("  1. -200 to 100 °C\n  2. -100 to 200 °C\n  3. 0 to 300 °C")
        choice = input("Choose range: ").strip()
        limits = [(-200, 100), (-100, 200), (0, 300)]
        tmin, tmax = limits[int(choice) - 1]

        temps = []
        resistances = []

        print("\nReading PT100. Press Ctrl+C to stop and plot...\n")
        try:
            while True:
                raw = self.read_raw()
                voltage = self.raw_to_voltage(raw)
                resistance = voltage / self.I
                temp = self.resistance_to_temperature(resistance)

                if tmin <= temp <= tmax:
                    print(f"Temp: {temp:.2f} °C | R: {resistance:.2f} Ω | V: {voltage:.3f} V")
                    temps.append(temp)
                    resistances.append(resistance)
                else:
                    print(f"⚠ Temp: {temp:.2f} °C is out of selected range ({tmin} to {tmax} °C)")

                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Plotting...")
            if temps and resistances:
                plt.plot(resistances, temps, 'r*-')
                plt.title("PT100 Temp vs Resistance")
                plt.xlabel("Resistance (Ω)")
                plt.ylabel("Temperature (°C)")
                plt.grid(True)
                plt.tight_layout()
                plt.show()
            else:
                print("No data within selected range to plot.")
