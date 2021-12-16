#! /usr/bin/env python3

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

PIN1 = 25
GPIO.setup(PIN1, GPIO.OUT)
GPIO.output(PIN1,True)

try:
	while True:
		time.sleep(0.5)
#		GPIO.output(PIN1, False)
#		time.sleep(0.5)
		GPIO.output(PIN1, True)
		pass
except KeyboardInterrupt:
	print()
	GPIO.output(PIN1, False)
	GPIO.cleanup()
	
