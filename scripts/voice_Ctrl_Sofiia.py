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
from std_msgs.msg import String, Float32, Int32, Bool
import threading
import numpy as np
from math import pi
from time import sleep
from yahboomcar_msgs.msg import *
from yahboomcar_msgs.srv import *
from geometry_msgs.msg import Twist
from dynamic_reconfigure.server import Server
from yahboomcar_bringup.cfg import PIDparamConfig
from sensor_msgs.msg import Imu, MagneticField, JointState
from voice_arm_library import *

from ultralytics import YOLO
import cv2 as cv
from visionworker import VisionWorker

WHISPER = whisper.load_model("base.en")
VOSK_PATH = "/root/data/shared/sofiia_ws/src/voice_ctrl_sofiia/models/vosk-model-small-en-us-0.15"
YOLO_PATH = "/root/data/shared/sofiia_ws/src/voice_ctrl_sofiia/models/my_model.pt"
VOSK = Model(VOSK_PATH)

class sofiia_car_driver:
    def __init__(self):
        rospy.on_shutdown(self.cancel)

        self.car = Rosmaster()
        self.factory = SpeechFactory()
        self.spe = self.factory.create_speech("whisper", WHISPER)
        self.voice_arm = Voice_Arm()
        self.car.set_car_type(2)
        self.last_update_time = 1
        self.pos = [0, 0, 0, 0]
        self.imu_link = rospy.get_param("~imu_link", "imu_link")
        self.Prefix = rospy.get_param("~prefix", "")
        self.xlinear_limit = rospy.get_param('~xlinear_speed_limit', 1.0)
        self.ylinear_limit = rospy.get_param('~ylinear_speed_limit', 1.0)
        self.angular_limit = rospy.get_param('~angular_speed_limit', 5.0)
        self.sub_cmd_vel = rospy.Subscriber('cmd_vel', Twist, self.cmd_vel_callback, queue_size=100)
        self.sub_RGBLight = rospy.Subscriber("RGBLight", Int32, self.RGBLightcallback, queue_size=100)
        self.sub_Buzzer = rospy.Subscriber("Buzzer", Bool, self.Buzzercallback, queue_size=100)
        self.sub_Arm = rospy.Subscriber("TargetAngle", ArmJoint, self.Armcallback, queue_size=1000)
        self.ArmPubUpdate = rospy.Publisher("ArmAngleUpdate", ArmJoint, queue_size=1000)
        self.EdiPublisher = rospy.Publisher('edition', Float32, queue_size=100)
        self.volPublisher = rospy.Publisher('voltage', Float32, queue_size=100)
        self.staPublisher = rospy.Publisher('joint_states', JointState, queue_size=100)
        self.velPublisher = rospy.Publisher("/pub_vel", Twist, queue_size=100)
        self.imuPublisher = rospy.Publisher("/pub_imu", Imu, queue_size=100)
        self.magPublisher = rospy.Publisher("/pub_mag", MagneticField, queue_size=100)
        self.srv_armAngle = rospy.Service("CurrentAngle", RobotArmArray, self.srv_Armcallback)
        self.dyn_server = Server(PIDparamConfig, self.dynamic_reconfigure_callback)
        self.car.create_receive_threading()
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

        #creating yolo model
        self.yolo_model = YOLO(YOLO_PATH)

        #start vision worker
        self.path_cam = '/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera-video-index0'
        self.vision = VisionWorker(self.path_cam, self.yolo_model, conf=0.45, imgsz=416)
        self.vision.start()
        self.win = "YOLO"
        self.state = "IDLE"

    def pub_data(self):
        ## Publish the speed of the car, gyroscope data, and battery voltage
        while not rospy.is_shutdown():
            sleep(0.05)
            imu = Imu()
            twist = Twist()
            battery = Float32()
            edition = Float32()
            mag = MagneticField()
            edition.data = self.car.get_version()
            battery.data = self.car.get_battery_voltage()
            ax, ay, az = self.car.get_accelerometer_data()
            gx, gy, gz = self.car.get_gyroscope_data()
            mx, my, mz = self.car.get_magnetometer_data()
            vx, vy, angular = self.car.get_motion_data()

            # Publish gyroscope data
            imu.header.stamp = rospy.Time.now()
            imu.header.frame_id = self.imu_link
            imu.linear_acceleration.x = ax
            imu.linear_acceleration.y = ay
            imu.linear_acceleration.z = az
            imu.angular_velocity.x = gx
            imu.angular_velocity.y = gy
            imu.angular_velocity.z = gz
            mag.header.stamp = rospy.Time.now()
            mag.header.frame_id = self.imu_link
            mag.magnetic_field.x = mx
            mag.magnetic_field.y = my
            mag.magnetic_field.z = mz
            
            # Publish the current linear vel and angular vel of the car
            twist.linear.x = vx
            twist.linear.y = vy
            twist.angular.z = angular
            self.velPublisher.publish(twist)
            
            self.imuPublisher.publish(imu)
            self.magPublisher.publish(mag)
            self.volPublisher.publish(battery)
            self.EdiPublisher.publish(edition)
            self.joints_states_update()

    def Armcallback(self, msg):
        if not isinstance(msg, ArmJoint): return
        arm_joint = ArmJoint()
        if len(msg.joints) != 0:
            arm_joint.joints = self.joints
            for i in range(2):
                self.car.set_uart_servo_angle_array(msg.joints, msg.run_time)
                self.joints = list(msg.joints)
                self.ArmPubUpdate.publish(arm_joint)
                sleep(0.01)
        else:
            arm_joint.id = msg.id
            arm_joint.angle = msg.angle
            for i in range(2):
                self.car.set_uart_servo_angle(msg.id, msg.angle, msg.run_time)
                self.joints[msg.id - 1] = msg.angle
                self.ArmPubUpdate.publish(arm_joint)
                sleep(0.01)
        self.joints_states_update()
        
        sleep(0.001)

    def srv_Armcallback(self, request):
        # Server, the current joint angle of the robotic arm
        if not isinstance(request, RobotArmArrayRequest): return
        
        response = RobotArmArrayResponse()
        joints = self.car.get_uart_servo_angle_array()
        response.angles = joints
        
        return response

    def RGBLightcallback(self, msg):
        if not isinstance(msg, Int32): return
        for i in range(3):
            self.car.set_colorful_effect(msg.data, 6, parm=1)
            sleep(0.01)

    def Buzzercallback(self, msg):
        #Buzzer control
        if not isinstance(msg, Bool): return
        
        if msg.data:
            for i in range(3):
                self.car.set_beep(1)
                sleep(0.01)
        else:
            for i in range(3):
                self.car.set_beep(0)
                sleep(0.01)

    def listen_speech(self):
        while not rospy.is_shutdown() and not self.spe.stop_evt.is_set():
            try: 
                speech_r = self.spe.speech_read()
                self.last_speech_cmd = speech_r
            except KeyboardInterrupt:
                break
            except Exception as e:
                rospy.logwarn(f"Speech thread error: {e}")
                if rospy.is_shutdown() or self.spe.stop_evt.is_set():
                    break
   
    def cmd_vel_callback(self,msg):
        # Car motion control, subscriber callback function
        if not isinstance(msg, Twist): return
        # Issue linear vel and angular vel
        vx = msg.linear.x
        vy = msg.linear.y
        angular = msg.angular.z
        self.car.set_car_motion(vx, vy, angular)
    
    def cancel(self):
        #stop camera thread
        if hasattr(self, "vision") and self.vision is not None:
            self.vision.stop()
            self.vision.join(timeout=1.0)

        self.spe.stop_stream()

        if hasattr(self, "speech_thread") and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)

        #turn off all
        self.car.set_colorful_effect(0, 6, parm=1)
        self.car.set_car_motion(0, 0, 0)
        self.car.set_beep(0)

        self.velPublisher.unregister()
        self.imuPublisher.unregister()
        self.EdiPublisher.unregister()
        self.volPublisher.unregister()
        self.staPublisher.unregister()
        self.magPublisher.unregister()
        self.sub_cmd_vel.unregister()
        self.sub_RGBLight.unregister()
        self.sub_Buzzer.unregister()
        # Always stop the robot when shutting down the node
        rospy.loginfo("Close the robot...")
        rospy.sleep(1)

    def joints_states_update(self):
        state = JointState()
        state.header.stamp = rospy.Time.now()
        state.header.frame_id = "joint_states"
        if len(self.Prefix) == 0:
            state.name = ["arm_joint1", "arm_joint2", "arm_joint3", "arm_joint4", "arm_joint5", "grip_joint"]
        else:
            state.name = [self.Prefix + "/arm_joint1", self.Prefix + "/arm_joint2",
                          self.init_posePrefix + "/arm_joint3", self.Prefix + "/arm_joint4",
                          self.Prefix + "/arm_joint5", self.Prefix + "/grip_joint"]
        joints = self.joints[:]
        joints[5] = np.interp(joints[5], [30, 180], [0, 90])
        mid = np.array([90, 90, 90, 90, 90, 90])
        array = np.array(np.array(joints) - mid)
        DEG2RAD = np.array([pi / 180])
        position_src = list(np.dot(array.reshape(-1, 1), DEG2RAD))
        state.position = position_src
        self.staPublisher.publish(state)

    def dynamic_reconfigure_callback(self, config, level):
        self.linear_max = config['linear_max']
        self.linear_min = config['linear_min']
        self.angular_max = config['angular_max']
        self.angular_min = config['angular_min']
        if config['SetArmjoint']:
            self.car.set_uart_servo_angle_array(
                [config['joint1'], config['joint2'], config['joint3'],
                 config['joint4'], config['joint5'], config['joint6']], run_time=1000)
        return config

    def go_ahead(self, sec):
        vx = 0.5
        vy = 0.0
        angular = 0
        self.car.set_car_motion(vx, vy, angular)
        rospy.sleep(sec)
        vx = 0
        vy = 0
        angular = 0  
        self.car.set_car_motion(vx, vy, angular)
    
    def main_loop(self):
        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            if self.last_speech_cmd is not None:
                #stop
                if self.last_speech_cmd == 0:
                    vx = 0.0
                    vy = 0.0
                    angular = 0
                    self.car.set_car_motion(vx, vy, angular)

                #go ahead
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
                    self.car.set_colorful_effect(6, 6, parm=1)

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
