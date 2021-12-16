import RPi.GPIO as GPIO
import os
import sys
import time

GPIO.setmode(GPIO.BCM)

PIN1 = 17
PIN2 = 18 #PWM
PIN3 = 27

GPIO.setup(PIN1,GPIO.OUT)
GPIO.setup(PIN2,GPIO.OUT)
pwm = GPIO.PWM(PIN2, 100)
GPIO.setup(PIN3,GPIO.OUT)

#GPIO.output(PIN1, True)
#GPIO.output(PIN2, False)
GPIO.output(PIN3, True)

pwm.start(0)
try:
	rate=0
	while True:
		rate = int(input("0~100%: "))
		pwm.ChangeDutyCycle(rate)

except KeyboardInterrupt:
	GPIO.output(PIN1, False)
	GPIO.output(PIN2, False)
	GPIO.output(PIN3, False)
	GPIO.cleanup()
	sys.exit()
