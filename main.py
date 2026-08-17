from ADS1256 import ADS1256

from sensors.moisture_sensor import MoistureSensor, get_ambient_temperature, run
from sensors.pressure_sensor import PiezoresistivePressureSensor
from sensors.pt100_sensor import SimulatedPT100
from sensors.vacuum_sensor import PfeifferVacuumSensor


### === Main Program Entry ===
def main():
    adc = ADS1256()
    adc.ADS1256_init()

    sensors = {
        "1": ("Moisture Sensor", MoistureSensor(adc)),
        "2": ("PT100 Temperature Sensor", SimulatedPT100(adc)),
        "3": ("Vacuum Sensor", PfeifferVacuumSensor(adc)),
        "4": ("Piezoresistive Pressure Sensor", PiezoresistivePressureSensor(adc)),
    }

    print("\nAvailable Sensors:")
    for key, (name, _) in sensors.items():
        print(f"  {key}. {name}")

    choice = input("Select sensor to run: ").strip()

    if choice == "1":
        ambient_temp = get_ambient_temperature()
        run(sensors["1"][1], ambient_temp)
    elif choice in sensors:
        print(f"\nStarting {sensors[choice][0]}...\n")
        sensors[choice][1].run()
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    main()
