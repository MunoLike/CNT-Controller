#! /usr/bin/env python3

import spidev
import time
import sys


spi = spidev.SpiDev()
spi.open(0,0)

spi.max_speed_hz=100_0000

while True:
	try:
		value = input("input duty[%]: ")
		value = int(int(value)/100*4095)
		spi.xfer2([0b00110000|(value>>8),0xFF&value])
		time.sleep(0.0001)
	except KeyboardInterrupt:
		spi.xfer2([0b00110000,0])
		spi.close()
		print()
		sys.exit()
		
	except:
		continue
		
