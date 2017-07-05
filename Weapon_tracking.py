#sudo modprobe bcm2835-v4l2

nimport cv2
import sys
import time
import RPi.GPIO as gpio
import numpy as np
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

red_lower=np.array([136,87,111],np.uint8)
red_upper=np.array([180,255,255],np.uint8)

blue_lower=np.array([99,115,150],np.uint8)
blue_upper=np.array([110,255,255],np.uint8)

yellow_lower=np.array([22,60,200],np.uint8)
yellow_upper=np.array([60,255,255],np.uint8)

#servo setup
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)

gpio.setup(37,gpio.OUT)
gpio.setup(35,gpio.OUT)

gpio.setup(38,gpio.OUT)

servo = gpio.PWM(37,50)
servo.start(7.5)
servo.ChangeDutyCycle(0)

servo_y = gpio.PWM(35,50)
servo_y.start(7.5)
servo_y.ChangeDutyCycle(0)

#arrays and such
currentPos = 111
CFacex = 10
max_right_pos = True
max_left_pos = True
minPos = 3
maxPos = 20
rangeRight = 300
rangeLeft = 290

currentPos_y = 111
CFacey = 10
max_right_pos_y = True
max_left_pos_y = True
minPos_y = 3
maxPos_y = 20
rangeRight_y = 300
rangeLeft_y = 290

incrementServo = 15

incrementServo_y = 15 

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                
def scan():
	if not max_right_pos: 
		servo_right()
		if currentPos >= maxPos:
			max_right_pos = True
			max_left_pos = False
	if not max_left_pos:
		servo_left()
		if currentPos <= minPos:
			max_right_pos = False
			max_left_pos = True 

def servo_left():
	if currentPos > minPos:
		currentPos = currentPos - incrementServo
		servo.ChangeDutyCycle(currentPos)
	time.sleep(.02)
	servo.ChangeDutyCycle(0) 

def servo_right():
	if currentPos < maxPos:
		currentPos = currentPos + incrementServo
		servo.ChangeDutyCycle(currentPos)
	time.sleep(.02)
	servo.ChangeDutyCycle(0)
	
def track_face(face_position):
        if face_position == rangeRight:
                time.sleep(.01)
                servo.ChangeDutyCycle(0)
        
        elif face_position > rangeRight:
                servo_left()

        elif face_position < rangeRight:
                servo_right()


def scan_y():
        
	if not max_right_pos_y:
		servo_right_y()
		if currentPos_y >= maxPos_y:
			max_right_pos_y = True
			max_left_pos_y = False

	if not max_left_pos_y:
		servo_left_y()
		if currentPos_y <= minPos_y:
			max_right_pos_y = False
			max_left_pos_y = True

def servo_left_y():
        
	if currentPos_y > minPos_y:
		currentPos_y = currentPos_y - incrementServo_y
		servo_y.ChangeDutyCycle(currentPos_y)
	time.sleep(.02)
	servo_y.ChangeDutyCycle(0)

def servo_right_y():
        
	if currentPos_y < maxPos_y:
		currentPos_y = currentPos_y + incrementServo_y
		servo_y.ChangeDutyCycle(currentPos_y)
	time.sleep(.02) 
	servo_y.ChangeDutyCycle(0)

def track_face_y(face_position_y):
        
        if face_position_y == rangeRight_y:
                time.sleep(.01)
                servo_y.ChangeDutyCycle(0)
        
        elif face_position_y > rangeRight_y:
                servo_left_y()

        elif face_position_y < rangeRight_y:
                servo_right_y()


def check_color(hsv):
        
        if c_l == 'g':
                green = cv2.inRange(hsv, greenLower, greenUpper)
                green = cv2.erode(green, None, iterations=2)
                green = cv2.dilate(green, None, iterations=2)

                cnts = cv2.findContours(green.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        elif c_l == 'r':
                red = cv2.inRange(hsv, red_lower, red_upper)
                red = cv2.erode(red, None, iterations=2)
                red = cv2.dilate(red, None, iterations=2)

                cnts = cv2.findContours(red.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        elif c_l == 'b':
                blue = cv2.inRange(hsv,blue_lower,blue_upper)
                blue = cv2.erode(blue, None, iterations=2)
                blue = cv2.dilate(blue, None, iterations=2)

                cnts = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        elif c_l == 'y':
                yellow = cv2.inRange(hsv,yellow_lower,yellow_upper)
                yellow = cv2.erode(yellow, None, iterations=2)
                yellow = cv2.dilate(yellow, None, iterations=2)

                cnts = cv2.findContours(yellow.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        return cnts

if not args.get("video", False):
	video_capture = cv2.VideoCapture(0)
 
else:
	video_capture = cv2.VideoCapture(args["video"])

while True:
        ret, frame = video_capture.read()

        if args.get("video") and not ret:
                break
        
        try:
                frame = imutils.resize(frame, width=600)
        except:
                continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cnts = check_color(hsv)

        center = None

        if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                if radius > 10:
                        cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                        cv2.circle(frame, center, 5, (0, 255, 0), -1)
                        print 'x-axis',int(x)
                        print 'y-axis',int(y)
                        CFacex = int(x)
                        CFacey = int(y)


        if stp == 0:
                if CFacex != 0:
                        track_face(CFacex)

                if CFacey != 0:
                        track_face_y(CFacey)

                else:
                        scan()
                        scan_y()

        cv2.putText(frame, "Q-exit, F-Fire, G-green, Y-yellow, R-red, B-blue", (5, frame.shape[0] - 5),cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2)
        cv2.namedWindow('Video', cv2.WINDOW_AUTOSIZE)
        #cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.imshow('Video', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('F'):
                gpio.output(38, True)
                time.sleep(5)
                gpio.output(38, False)

        elif key == ord('G'):
                c_l = 'g'

        elif key == ord('R'):
                c_l = 'r'

        elif key == ord('B'):
                print 'b'
                c_l = 'b'

        elif key == ord('Y'):
                c_l = 'y'

        elif key == ord('Q'):
                break

        CFacex = 0
        CFacey = 0

# clean up
gpio.cleanup()
video_capture.release()
cv2.destroyAllWindows()

	
