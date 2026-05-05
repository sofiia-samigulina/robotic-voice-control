#!/usr/bin/env python3
from Rosmaster_Lib import Rosmaster
from time import sleep
import threading

car = Rosmaster()
car.set_car_type(2)
car.create_receive_threading()
sleep(1.0)

stop_monitor = threading.Event()
voltage_log = []

def monitor_voltage():
    while not stop_monitor.is_set():
        v = car.get_battery_voltage()
        voltage_log.append(v)
        print(f"  [VOLTAGE] {v:.3f}V")
        sleep(0.2)

monitor_thread = threading.Thread(target=monitor_voltage)
monitor_thread.daemon = True
monitor_thread.start()

print(f"Start battery level: {car.get_battery_voltage():.3f}V\n")

#test servo 1
# 1: → 160
#for _ in range(0, 4):
#    print("--- Joint 1 → 160 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(1, 160, 1000)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(1)
#    print(f"Res: {angle} (expected 160)")
#    print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

#    # 2: → 6
#    print("\n--- Joint 1 → 6 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(1, 6, 1000)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(1)
#    print(f"Res: {angle} (expected 6)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#    #  3: → 90
#    print("\n--- Joint 1 → 90 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(1, 90, 1000)
#    sleep(4.0)
#    angle = car.get_uart_servo_angle(1)
#    print(f"Res: {angle} (expected 90)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")


#test servo 2
#for _ in range (0, 4):
#    # 1: → 90
#    print("--- Joint 2 → 90 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(2, 90, 1500)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(2)
#    print(f"Res: {angle} (expected 90)")
#    print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

    # 2: → 6
#    print("\n--- Joint 2 → 6 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(2, 6, 1500)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(2)
#    print(f"Res: {angle} (expected 6)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

    #  3: → 90
#    print("\n--- Joint 2 → 90 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(2, 90, 1500)
#    sleep(4.0)
#    angle = car.get_uart_servo_angle(2)
#    print(f"Res: {angle} (expected 90)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#test servo 3

#for _ in range(0,4):
#    # 1: → 90
#    print("--- Joint 3 → 90 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(3, 90, 500)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(3)
#    print(f"Res: {angle} (expected 90)")
#    print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

# 2: → 6
#    print("\n--- Joint 3 → 10 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(3, 10, 500)
#    sleep(2.0)
#    angle = car.get_uart_servo_angle(3)
#    print(f"Res: {angle} (expected 10)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#  3: → 90
#    print("\n--- Joint 3 → 90 ---")
#    v_before = car.get_battery_voltage()
#    car.set_uart_servo_angle(3, 90, 500)
#    sleep(4.0)
#    angle = car.get_uart_servo_angle(3)
#    print(f"Res: {angle} (expected 90)")
#    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#test servo 4
# 1: → 90
#print("--- Joint 4 → 90 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(4, 90, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(4)
#print(f"Res: {angle} (expected 90)")
#print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

# 2: → 6
#print("\n--- Joint 4 → 6 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(4, 4, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(4)
#print(f"Res: {angle} (expected 6)")
#print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#  3: → 90
#print("\n--- Joint 4 → 90 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(4, 90, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(4)
#print(f"Res: {angle} (expected 90)")
#print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#test servo 5
# 1: → 160
#print("--- Joint 5 → 160 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(5, 160, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(5)
#print(f"Res: {angle} (expected 160)")
#print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

# 2: → 6
#print("\n--- Joint 5 → 6 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(5, 6, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(5)
#print(f"Res: {angle} (expected 6)")
#print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#  3: → 90
#print("\n--- Joint 5 → 90 ---")
#v_before = car.get_battery_voltage()
#car.set_uart_servo_angle(5, 90, 500)
#sleep(2.0)
#angle = car.get_uart_servo_angle(5)
#print(f"Res: {angle} (expected 90)")
#print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

#test servo 6
for _ in range (0, 4):
    # 1: → 175
    print("--- Joint 6 → 175 ---")
    v_before = car.get_battery_voltage()
    car.set_uart_servo_angle(6, 175, 500)
    sleep(2.0)
    angle = car.get_uart_servo_angle(6)
    print(f"Res: {angle} (expected 175)")
    print(f"Voltage drop: {v_before - car.get_battery_voltage():.3f}V")

    # 2: → 6
    print("\n--- Joint 6 → 6 ---")
    v_before = car.get_battery_voltage()
    car.set_uart_servo_angle(6, 6, 500)
    sleep(2.0)
    angle = car.get_uart_servo_angle(6)
    print(f"Res: {angle} (expected 6)")
    print(f"Battery drop: {v_before - car.get_battery_voltage():.3f}V")

# Итог
stop_monitor.set()
monitor_thread.join(timeout=1.0)
