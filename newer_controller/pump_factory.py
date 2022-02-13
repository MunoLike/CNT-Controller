from abc import abstractmethod
import os

class Pump:
    @abstractmethod
    def change_ratio(self, ratio):
        pass

class PeristalticPump(Pump):
    def __init__(self):
        import spidev
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 100_000

        self.value = 0

    def change_ratio(self, ratio: int):
        import spidev
        if ratio > 100:
            print('PWM Ratio out of range:', ratio)
            return
        if ratio < 0:
            print('PWM Ratio out of range:', ratio)
            return

        value = int(int(value)/100*4095)
        self.spi.xfer2([0b00110000 | (value >> 8), 0xFF & value])

    def __del__(self):
        import spidev
        self.spi.xfer2([0b00110000,0])
        self.spi.close()

class DummyPump(Pump):
    def change_ratio(self, ratio: int):
        if ratio > 100:
            print('PWM Ratio out of range:', ratio)
            return
        if ratio < 0:
            print('PWM Ratio out of range:', ratio)
            return


def create_pump() -> Pump:
    if os.name == 'nt':
        return DummyPump()
    elif os.name =='posix':
        return PeristalticPump()