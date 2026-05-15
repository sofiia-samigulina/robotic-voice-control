import rospy
from time import sleep
from yahboomcar_msgs.msg import *

class Voice_Arm:
    def __init__(self, car):
        rospy.on_shutdown(self.cancel)
        self.pubPoint = rospy.Publisher("TargetAngle", ArmJoint, queue_size=1)

        #initialization
        self.car = car
        self.arm_joint = ArmJoint()
        self.arm_joint.id = 6
        self.arm_joint.angle = 180
        self.arm_joint.run_time = 500

    def init_pose(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_up(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[94.0, 93.0, 92.0, 88.0, 93.0, 175.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_down(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90.0, 6.0, 90.0, 88.0, 93.0, 175.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_left(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[5.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_right(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[175.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_clamping(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[89.0, 179.0, 0.0, 0.0, 90.0, 150.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_loosen(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[89.0, 179.0, 0.0, 0.0, 90.0, 35.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_dance(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90, 90, 90, 90, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90, 60, 120, 60, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 45, 135, 45, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 60, 120, 60, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 90, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 100, 80, 80, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 120, 60, 60, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 135, 45, 45, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 90, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 20, 90, 150]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 90, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 20, 90, 150]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[0, 90, 90, 90, 0, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[0, 90, 180, 0, 0, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints = []
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 90, 90, 90, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90, 135, 0, 45, 90, 90]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_nod(self):
        self.arm_joint.run_time = 500
        for _ in range(3):
            self.arm_joint.joints =[82.0, 89.0, 93.0, 93.0, 89.0, 32.0]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
            self.arm_joint.joints =[82.0, 89.0, 93.0, 33.0, 89.0, 32.0]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)

        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_kneel_down(self):
        self.arm_joint.run_time = 500
        for _ in range(3):
            self.arm_joint.joints =[90, 11, 179, 0, 90, 33]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
            self.arm_joint.joints =[90, 11, 179, 0, 90, 161]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
        
    def arm_applaud(self):
        self.arm_joint.run_time = 500
        for _ in range(3):
            self.arm_joint.joints =[90.0, 145.0, 0.0, 71.0, 90.0, 31.0] 
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
            self.arm_joint.joints =[91.0, 144.0, 0.0, 71.0, 90.0, 168.0]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)

        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_stack(self):
        self.arm_joint.run_time = 500
        for i in range(3):      		
            self.arm_joint.joints = [90.0, 144.0, 0.0, 44.0, 90.0, 71.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)
            
            self.arm_joint.joints = [90.0, 144.0, 0.0, 44.0, 91.0, 128.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)
            
            self.arm_joint.joints = [7.0, 144.0, 0.0, 44.0, 90.0, 128.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)
            
            joint4 = 68 + i * 8
            self.arm_joint.joints = [7.0, 0.0, 98.0, joint4, 90.0, 128.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)
           
            self.arm_joint.joints = [7.0, 0.0, 98.0, joint4, 90.0, 71.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)
            
            self.arm_joint.joints = [7.0, 38.0, 90.0, 90.0, 90.0, 72.0]
            self.pubPoint.publish(self.arm_joint)
            sleep(1.0)

            if i == 2:
               self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
               self.pubPoint.publish(self.arm_joint)
               sleep(0.5)	

    def arm_pray(self):
        self.arm_joint.run_time = 500
        self.arm_joint.joints = [90, 120, 0, 0, 90, 30]  
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_scare(self):
        self.arm_joint.run_time = 500
        for _ in range(3):
            self.arm_joint.joints =[138.0, 94.0, 92.0, 88.0, 92.0, 172.0]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
            self.arm_joint.joints =[48.0, 94.0, 92.0, 87.0, 92.0, 172.0]
            self.pubPoint.publish(self.arm_joint)    
            sleep(1.0)
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_wait_the_object(self):
        self.arm_joint.run_time = 1000
        self.arm_joint.joints = [90, 145, 0, 45, 90, 30]
        self.pubPoint.publish(self.arm_joint)
        sleep(1.0)

    def arm_grip_object(self, position):
        self.arm_joint.joints = [position, 145, 0, 45, 90, 134]
        self.arm_joint.run_time = 500
        self.pubPoint.publish(self.arm_joint)
        sleep(0.5)
        self.arm_joint.joints = [90, 145, 0, 45, 90, 134]
        self.arm_joint.run_time = 500
        self.pubPoint.publish(self.arm_joint)
        sleep(0.5)

    def arm_rotate(self, position, run_time_ms):
        self.arm_joint.joints = [position, 145, 0, 45, 90, 30]
        self.arm_joint.run_time = run_time_ms
        self.pubPoint.publish(self.arm_joint)

    def arm_put_object(self):
        self.arm_joint.joints = [90, 2, 60, 40, 90, 134]
        self.arm_joint.run_time = 1500
        self.pubPoint.publish(self.arm_joint)
        sleep(1.5)
        self.arm_joint.joints = [90, 2, 60, 40, 90, 30]
        self.arm_joint.run_time = 500
        self.pubPoint.publish(self.arm_joint)
        sleep(0.5)
        self.arm_joint.joints = [90, 145, 0, 45, 90, 30]
        self.arm_joint.run_time = 2000
        self.pubPoint.publish(self.arm_joint)
        sleep(2.5)
        self.arm_joint.run_time = 500
        self.arm_joint.joints =[90.0, 145.0, 0.0, 0.0, 90.0, 31.0]
        self.pubPoint.publish(self.arm_joint)
        sleep(0.5)


    def cancel(self):
        self.pubPoint.unregister()
