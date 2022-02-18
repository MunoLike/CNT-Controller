from abc import abstractmethod
import os

class Pump:
    @abstractmethod
    def change_ratio(self, ratio):
        pass

    @abstractmethod
    def close(self):
        pass

class PeristalticPump(Pump):
    LED_PIN = 25 # LED pin

    def __init__(self):
        import spidev
        import RPi.GPIO as GPIO
        #LED setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PeristalticPump.LED_PIN, GPIO.OUT)
        GPIO.output(PeristalticPump.LED_PIN,True)
        GPIO.output(PeristalticPump.LED_PIN, True)
        #pump setup
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 100_000

    def change_ratio(self, ratio: int):
        import spidev
        if ratio > 100:
            print('Pump Ratio out of range:', ratio)
            return
        if ratio < 0:
            print('Pump Ratio out of range:', ratio)
            return

        value = int(int(value)/100*4095)
        self.spi.xfer2([0b00110000 | (value >> 8), 0xFF & value])

    def close(self):
        import RPi.GPIO as GPIO
        import spidev
        # turn the backlight off
        GPIO.output(PeristalticPump.LED_PIN, False)
        GPIO.cleanup()
        # close pump
        self.spi.xfer2([0b00110000,0])
        self.spi.close()

class DummyPump(Pump):
    def change_ratio(self, ratio: int):
        if ratio > 100:
            print('Pump Ratio out of range:', ratio)
            return
        if ratio < 0:
            print('Pump Ratio out of range:', ratio)
            return
    def close(self):
        print('pump closed')


def create_pump() -> Pump:
    if os.name == 'nt':
        return DummyPump()
    elif os.name =='posix':
        return PeristalticPump()