import time
import RPi.GPIO as GPIO
import spidev




sensor_file = '/sys/bus/w1/devices/28-051673ac35ff/w1_slave'

spi = spidev.SpiDev()
spi.open(0, 0)

led = 16




class readSensor():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(led, GPIO.OUT)

    def getAdc(self, channel):
        # check valid channel
        if ((channel > 7) or (channel < 0)):
            return -1
        # Preform SPI transaction and store returned bits in 'r'
        r = spi.xfer([1, (8 + channel) << 4, 0])
        # Filter data bits from retruned bits
        adcOut = ((r[1] & 3) << 8) + r[2]
        percent = int(round(adcOut / 10.24))
        # print out 0-1023 value and percentage
        return percent
        # time.sleep(0.1)

    def read_temp_raw(self):
        f = open(sensor_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            return lines[1]

    def print_temp(self):
        line = self.read_temp()
        temp = line.split('t=')[1]
        temp = float(temp) / 1000.0
        return temp

