import time
import math
import matplotlib.pyplot as plt
from ADS1256 import ADS1256

# === Moisture Sensor Class ===
class MoistureSensor:
    def __init__(self, adc, channel=0, vref=5.0, resistor=220, current_range=(4.0, 20.0), ppm_max=13000):
        self.adc = adc
        self.channel = channel
        self.vref = vref
        self.resistor = resistor
        self.current_min, self.current_max = current_range
        self.ppm_max = ppm_max

        self.points_current = [4.0, 5.07, 6.13, 7.20, 8.27, 9.33, 10.40, 11.47,
                               12.53, 13.60, 14.67, 15.73, 16.80, 17.87, 18.93, 20.0]
        self.points_ppm = [0, 900, 1700, 2700, 3600, 4600, 5500, 6500,
                           7600, 8600, 9700, 10800, 11800, 12400, 12800, 13000]

    def read_raw(self):
        return self.adc.ADS1256_GetChannalValue(self.channel)

    def raw_to_voltage(self, raw):
        if raw & 0x800000:
            raw -= 1 << 24
        return (raw / float(0x7FFFFF)) * self.vref

    def voltage_to_current(self, voltage):
        return (voltage / self.resistor) * 1000  # mA

    def current_to_moisture(self, current):
        if current < self.points_current[0]:
            return 0
        if current > self.points_current[-1]:
            return self.ppm_max
        for i in range(len(self.points_current) - 1):
            if self.points_current[i] <= current <= self.points_current[i + 1]:
                x0, x1 = self.points_current[i], self.points_current[i + 1]
                y0, y1 = self.points_ppm[i], self.points_ppm[i + 1]
                return y0 + (current - x0) * (y1 - y0) / (x1 - x0)
        return 0

    def moisture_to_rh(self, moisture):
        rh = (moisture / self.ppm_max) * 100
        return min(max(rh, 0), 100)

    def dew_point(self, T, RH):
        RH = max(1.0, RH)
        a = 17.27
        b = 237.7
        alpha = ((a * T) / (b + T)) + math.log(RH / 100.0)
        dp = (b * alpha) / (a - alpha)
        return max(-20.0, min(dp, 110.0))


def get_ambient_temperature():
    while True:
        try:
            return float(input("Enter ambient temperature in °C: "))
        except ValueError:
            print("Invalid input. Please enter a number.")


def select_display_mode():
    print("\nSelect display mode:")
    print("  1. Relative Humidity (%)")
    print("  2. Dew Point (°C)")
    print("  3. Moisture (PPM)")
    while True:
        mode = input("Enter choice (1/2/3): ").strip()
        if mode in ("1", "2", "3"):
            return mode
        print("Invalid choice. Try again.")


def run(sensor: MoistureSensor, ambient_temp: float):
    mode = select_display_mode()
    currents = []
    values = []

    print("\nRunning Moisture Sensor...")
    print("Press Ctrl+C to stop and plot data.\n")

    try:
        while True:
            raw = sensor.read_raw()
            voltage = sensor.raw_to_voltage(raw)
            current = sensor.voltage_to_current(voltage)
            moisture = sensor.current_to_moisture(current)
            rh = sensor.moisture_to_rh(moisture)
            dp = sensor.dew_point(ambient_temp, rh)

            if mode == "1":
                print(f"RH: {rh:.2f} % | Current: {current:.2f} mA")
                values.append(rh)
                ylabel = "Relative Humidity (%)"
            elif mode == "2":
                print(f"Dew Point: {dp:.2f} °C | RH: {rh:.2f} % | Moisture: {moisture:.0f} ppm")
                values.append(dp)
                ylabel = "Dew Point (°C)"
            elif mode == "3":
                print(f"Moisture: {moisture:.0f} ppm | Current: {current:.2f} mA")
                values.append(moisture)
                ylabel = "Moisture (ppm)"

            currents.append(current)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nMeasurement stopped. Plotting against Current...")

        if not values:
            print("No data to plot.")
            return

        plt.figure(figsize=(8, 5))
        plt.plot(currents, values, marker='o', color='green')
        plt.xlabel("Current (mA)")
        plt.ylabel(ylabel)
        plt.title(f"{ylabel} vs Current")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
