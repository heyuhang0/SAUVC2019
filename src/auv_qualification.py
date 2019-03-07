import time
import argparse
from mcu import MCU
from imu import IMU
from pid import *

def add_list(list1, list2, list3 ,list4):
    finalListValues = []
    for i in range(5):
        a = list1[i]
        b = list2[i]
        c = list3[i]
        d = list4[i]

        finalValues = a + b + c + d
        finalListValues.append(finalValues)
    return finalListValues

def main():
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--speed")
    ap.add_argument("-a", "--angle")
    args = vars(ap.parse_args())

    speed = args.get('speed', 0)
    if speed is None:
        speed = 0
    speed = float(speed)

    angle = args.get('angle', 0)
    if angle is None:
        angle = 0
    angle = float(angle)

    # inits MCU
    mcu = MCU(2222)

    # inits IMU
    imu = IMU("/dev/ttyUSB_IMU")

    mcu.start()
    imu.start()

    time.sleep(2)
    imu.delta_yaw = imu.get_yaw()
    print('Target yaw: ', imu.delta_yaw)

    mcu.wait()

    pidR = pidRoll(1, 0, 0) # 5, 0.1 , 5
    pidP = pidPitch(1, 0, 0)# 5 ,0.1 ,8
    pidD = pidDepth(1, 0, 0)
    pidY = pidYaw(1, 0.2, 0)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        counter = 0
        while True:
            counter += 1
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()
            yaw = imu.get_yaw()

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(70-depth)
            pidY.getSetValues(-yaw)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values #/ 4
                sentValues.append(subValues)

            motor_fl = sentValues[0]
            motor_fr = sentValues[1]
            motor_bl = sentValues[2] + speed
            motor_br = sentValues[3] + speed
            motor_t = sentValues[4]

            # Put control codes here

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)
            
            if counter % 20 == 0:
                print('Depth:', depth)
                print('Pinger:', pinger)
                print('Pitch:', pitch)
                print('Roll:', roll)
                print('Yaw:', yaw)
                print('Motors: %.2f %.2f %.2f %.2f %.2f'%(motor_fl, motor_fr, motor_bl, motor_br, motor_t))
                print()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        imu.stop()
        mcu.stop()

if __name__ == '__main__':
    main()
