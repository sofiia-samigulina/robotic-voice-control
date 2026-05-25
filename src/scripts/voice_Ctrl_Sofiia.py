#!/usr/bin/env python3

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../my_libs')))

from speech_factory import SpeechFactory
import whisper
from vosk import Model
from Rosmaster_Lib import Rosmaster

import rospy
from std_msgs.msg import Float32
import threading
import numpy as np
from math import pi
from time import sleep
from yahboomcar_msgs.msg import *
from yahboomcar_msgs.srv import *
from sensor_msgs.msg import JointState
from voice_arm_library import *

from ultralytics import YOLO
from visionworker import VisionWorker

WHISPER = whisper.load_model("base.en")
VOSK_PATH = "/root/data/shared/sofiia_ws/src/voice_ctrl_sofiia/models/vosk-model-small-en-us-0.15"
YOLO_PATH = "/root/data/shared/sofiia_ws/src/voice_ctrl_sofiia/models/my_model.pt"
VOSK = Model(VOSK_PATH)

car = Rosmaster()
factory = SpeechFactory()
spe = factory.create_speech("Vosk", VOSK)
sleep(1.0)

class sofiia_car_driver:
    def __init__(self):
        rospy.on_shutdown(self.cancel)

        #inicialization of car
        self.car = car
        self.car.set_car_type(2)

        #inicialization of speech
        self.spe = spe

        #creating of voice_arm
        self.voice_arm = Voice_Arm(self.car)
       
        #subscribers
        self.sub_Arm = rospy.Subscriber("TargetAngle", ArmJoint, self.Armcallback, queue_size=1000)
        self.sub_Battery = rospy.Subscriber('voltage', Float32, self.battery_callback)
        
        #publishers
        self.volPublisher = rospy.Publisher('voltage', Float32, queue_size=100)

        self.car.create_receive_threading()

        #start pose of the car
        self.car.set_car_motion(0, 0, 0)
        self.joints = [90, 145, 0, 0, 90, 30]
        self.car.set_uart_servo_angle_array(self.joints, 1000)

        self.rotate_arm = 90
        self.run_time_ms = 0

        self.last_speech_cmd = None

        #thread for speech recognition
        self.speech_thread = threading.Thread(target=self.listen_speech)
        self.speech_thread.daemon = True
        self.speech_thread.start()

        #thread for battery
        self.pub_battery = threading.Thread(target=self.pub_battery_voltage)
        self.pub_battery.daemon = True
        self.pub_battery.start()
        self.battery_voltage = 0.0

        #creating yolo model
        self.yolo_model = YOLO(YOLO_PATH)

        #start vision worker
        self.path_cam = '/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera-video-index0'
        self.vision = VisionWorker(self.path_cam, self.yolo_model, conf=0.45, imgsz=416)
        self.vision.start()
        self.win = "YOLO"
        self.state = "IDLE"

        #latency
        self.start = 0
        self.end = 0

        #go forward
        self.go_ahead_until = 0

    def pub_battery_voltage(self):
        ## Publish the battery voltage
        while not rospy.is_shutdown() and not self.spe.stop_evt.is_set():
            sleep(0.05)
            battery = Float32()
            battery.data = self.car.get_battery_voltage()
            self.volPublisher.publish(battery)

    def battery_callback(self, msg):
        self.battery_voltage = msg.data

    def Armcallback(self, msg):
        if not isinstance(msg, ArmJoint): return
        if len(msg.joints) != 0:
            self.car.set_uart_servo_angle_array(msg.joints, msg.run_time)
            self.end = time.perf_counter()
        else:
            self.car.set_uart_servo_angle(msg.id, msg.angle, msg.run_time)
            self.end = time.perf_counter()

        #but we need only first log in the commands where are a lot of actions
        #if self.end !=0:
        #    rospy.loginfo(f"Speech recognition latency: {self.end - self.start}")

        sleep(0.001)

    def listen_speech(self):
        while not rospy.is_shutdown() and not self.spe.stop_evt.is_set():
            try: 
                result = self.spe.speech_read()

                if result is None:
                    continue

                if not isinstance(result, tuple) or len(result) != 2:
                    continue

                self.last_speech_cmd, self.start = result
            except KeyboardInterrupt:
                break
            except Exception as e:
                rospy.logwarn(f"Speech thread error: {e}")
                if rospy.is_shutdown() or self.spe.stop_evt.is_set():
                    break
    
    def cancel(self):
        #turn off all
        self.car.set_colorful_effect(0, 6, parm=1)
        self.car.set_car_motion(0, 0, 0)
        self.car.set_beep(0)

        #stop camera thread
        if hasattr(self, "vision") and self.vision is not None:
            self.vision.stop()
            self.vision.join(timeout=1.0)

        #stop speech thread
        self.spe.stop_stream()
        if hasattr(self, "speech_thread") and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)

        #stop battery thread
        if hasattr(self, "pub_battery") and self.pub_battery.is_alive():
            self.pub_battery.join(timeout=1.0)

        self.sub_Arm.unregister()
        self.sub_Battery.unregister()
        self.volPublisher.unregister()

        # Always stop the robot when shutting down the node
        rospy.loginfo("Close the robot...")
        rospy.sleep(1)

    def go_ahead(self, sec):
        vx = 0.5
        vy = 0.0
        angular = 0
        self.car.set_car_motion(vx, vy, angular)
        self.go_ahead_until = time.perf_counter() + sec

    def main_loop(self):
        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            if self.go_ahead_until > 0:
                if time.perf_counter() >= self.go_ahead_until:
                    #stop the car
                    self.car.set_car_motion(0, 0, 0)
                    self.go_ahead_until = 0

            if self.last_speech_cmd is not None:

                #stop bude fungovat ak hovorit hlasnejsie
                if self.last_speech_cmd == 0:
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)
                    self.go_ahead_until = 0

                #go forward
                elif self.last_speech_cmd == 1:
                    self.go_ahead(3)

                #back
                elif self.last_speech_cmd == 2:
                    vx = -0.5
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)
                    rospy.sleep(3)
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)

                #turn left
                elif self.last_speech_cmd == 3:
                    vx = 0.2
                    vy = 0.0
                    angular = 0.5
                    self.car.set_car_motion(vx, vy, angular)
                    rospy.sleep(4)
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)

                #turn right
                elif self.last_speech_cmd == 4:
                    vx = 0.2
                    vy = 0.0
                    angular = -0.5
                    self.car.set_car_motion(vx, vy, angular) 
                    rospy.sleep(4)
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)

                #Enter A mode
                elif self.last_speech_cmd == 5:
                    vx = 0.0
                    vy = 0.0
                    angular = 0.5
                    self.car.set_car_motion(vx, vy, angular)
                    rospy.sleep(4)
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)

                #Enter B mode
                elif self.last_speech_cmd == 6:
                    vx = 0.0
                    vy = 0.0
                    angular = -0.5
                    self.car.set_car_motion(vx, vy, angular)
                    rospy.sleep(4)
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)
            
                #close light
                elif self.last_speech_cmd == 7:
                    self.car.set_colorful_effect(0, 6, parm=1)

                #red light up
                elif self.last_speech_cmd == 8:
                    self.car.set_colorful_lamps(0xFF,255,0,0) 
                
                #green light up
                elif self.last_speech_cmd == 9:
                    self.car.set_colorful_lamps(0xFF,0,255,0)

                #blue light up
                elif self.last_speech_cmd == 10:
                    self.car.set_colorful_lamps(0xFF,0,0,255)
    
                #yellow light up
                elif self.last_speech_cmd == 11:
                    self.car.set_colorful_lamps(0xFF,255,255,0)

                #light A
                elif self.last_speech_cmd == 12:
                    self.car.set_colorful_effect(1, 6, parm=1)
                
                #light B
                elif self.last_speech_cmd == 13:
                    self.car.set_colorful_effect(4, 6, parm=1)

                #light C
                elif self.last_speech_cmd == 14:
                    self.car.set_colorful_effect(3, 6, parm=1)

                #display battery value
                elif self.last_speech_cmd == 15:
                    if self.battery_voltage >= 11.8:
                        self.car.set_colorful_lamps(0xFF,0,255,0)
                    elif 11.0 >= self.battery_voltage < 11.8:
                        self.car.set_colorful_lamps(0xFF,255,255,0)
                    elif self.battery_voltage < 11.0:
                        self.car.set_colorful_lamps(0xFF,255,0,0)
                    
                    rospy.loginfo(f"My battery is: {self.battery_voltage:.2f} V")

                #beep 3 times
                elif self.last_speech_cmd == 16:
                    for i in range(3):
                        self.car.set_beep(1)
                        sleep(1)
                        self.car.set_beep(0)
                        sleep(1)

                #move arm up
                elif self.last_speech_cmd == 17:
                    self.voice_arm.arm_up()

                #move arm down
                elif self.last_speech_cmd == 18:
                    self.voice_arm.arm_down()
        
                #hand left
                elif self.last_speech_cmd == 19:
                    self.voice_arm.arm_left() 

                #hand right
                elif self.last_speech_cmd == 20:
                    self.voice_arm.arm_right() 
             
                #close the grip
                elif self.last_speech_cmd == 21:
                    self.voice_arm.arm_clamping()  

                #open the grip
                elif self.last_speech_cmd == 22:
                    self.voice_arm.arm_loosen() 

                #applause
                elif self.last_speech_cmd == 23:
                   self.voice_arm.arm_applaud()

                #up down up down
                elif self.last_speech_cmd == 24:
                   self.voice_arm.arm_nod()

                #meditate
                elif self.last_speech_cmd == 25:
                    self.voice_arm.arm_pray()

                #kneel down
                elif self.last_speech_cmd == 26:
                    self.voice_arm.arm_kneel_down()

                #neutral pose
                elif self.last_speech_cmd == 27:
                    self.voice_arm.init_pose()

                #scare
                elif self.last_speech_cmd == 28:
                    self.voice_arm.arm_scare()

                #stack
                elif self.last_speech_cmd == 29:
                    self.voice_arm.arm_stack()
  
                #dance
                elif self.last_speech_cmd == 30:
                    self.voice_arm.arm_dance()

                #move the object
                elif self.last_speech_cmd == 31:

                    #prepare arm for searching and grabbing
                    self.voice_arm.arm_wait_the_object()

                    self.vision.flush_camera();

                    #searching the object
                    self.vision.start_search()
                    self.state = 'SEARCHING'

                    print("Searching the cube...")  

                    while not rospy.is_shutdown() and self.state != "GRABBING":
                        if self.last_speech_cmd == 32:
                            self.voice_arm.init_pose()
                            break

                        det = self.vision.get_det()
                        if det is None:
                            self.state = "SEARCHING"
                            self.vision.start_search()
                            rospy.sleep(0.02)
                            continue
                        
                        xyxy, conf, ts = det

                        if time.time() - ts > 0.2:
                            self.state = "SEARCHING"
                            self.vision.start_search()
                            continue
                    
                        if xyxy is not None and conf is not None:
                            print("Detected cube:", xyxy)
                            print("Conf:", conf)

                            cube_center = (xyxy[2] + xyxy[0]) / 2
                            dead_px = 10
                            err = abs(cube_center - self.vision.frame_center)

                            if err > dead_px:

                                koefficient = 0.015
                                step = min((err * koefficient), 3)

                                old_angle = self.rotate_arm

                                max_speed_deg_per_sec = 30

                                if self.vision.frame_center > cube_center:      
                                    self.rotate_arm -= step
                                    if self.rotate_arm < 5:
                                        self.rotate_arm = 5
                                    
                                elif self.vision.frame_center < cube_center:  
                                    self.rotate_arm += step
                                    if self.rotate_arm > 175:
                                        self.rotate_arm = 175
                                    
                                delta = abs(self.rotate_arm - old_angle)
                                self.run_time_ms = max(150, int(delta / max_speed_deg_per_sec * 1000))
                                self.run_time_ms = min(self.run_time_ms, 800)

                                if abs(self.rotate_arm - old_angle) >= 1:
                                    self.voice_arm.arm_rotate(self.rotate_arm, self.run_time_ms)

                            if conf >= 0.90 and (xyxy[1] >= 210 and (xyxy[2]-xyxy[0]) >= 265) and (7 <= xyxy[0] <= 350):
                                self.state = "GRABBING"
                            else:
                                self.state = "SEARCHING"
                                self.vision.start_search()

                        rospy.sleep(0.02)
                    
                    self.vision.search_evt.clear()

                    if self.state == "GRABBING":
                        self.voice_arm.arm_grip_object(self.rotate_arm)
                        self.car.set_beep(1)
                        sleep(0.5)
                        self.car.set_beep(0)
                        self.go_ahead(2)
                        self.voice_arm.arm_put_object()

                    self.state = "IDLE"

                self.last_speech_cmd = None

            rate.sleep()

if __name__ == '__main__':
    rospy.init_node("driver_node", anonymous=False)
    driver = sofiia_car_driver()
    try:
        driver.main_loop()
    except KeyboardInterrupt:
        print("Close!")
        rospy.signal_shutdown("KeyboardInterrupt")
