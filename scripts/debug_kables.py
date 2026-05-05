#!/usr/bin/env python3
from Rosmaster_Lib import Rosmaster
from time import sleep

car = Rosmaster()
car.set_car_type(2)
car.create_receive_threading()
sleep(1.0)

#car.set_car_motion(0.3, 0, 0)  # поехать вперёд
#sleep(2.0)
#car.set_car_motion(0, 0, 0)

#print(car.get_battery_voltage())   # отвечает?
#print(car.get_version())

while True:
    print(car.get_uart_servo_angle_array())
    sleep(0.5)
