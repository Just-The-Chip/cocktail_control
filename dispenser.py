#I2C Pins
#GPIO2 -> SDA
#GPIO3 -> SCL
# pump:jarpos:ms
# flush

from RPi import GPIO
import smbus
import time
import subprocess

class Dispenser:

    def __init__(self, address, **kwargs):
        self.address = address
        self.msPerOz = kwargs.get('mspoz', 1000)
        self.prime = kwargs.get('prime', {})

        self.bus = smbus.SMBus(1) # for RPI version 1, use "bus = smbus.SMBufs(0)"
        self.spin = kwargs.get('spin', 10)
        self.dpin = kwargs.get('dpin', 11)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.spin, GPIO.IN)
        GPIO.setup(self.dpin, GPIO.IN)

    def writeBlock(self, string):  #This sends the command.  First byte sent is the number of characters in the command.
        value = list(map(ord, string))

        try:
            self.bus.write_i2c_block_data(self.address, len(value), value)
            return -1
        except OSError as err:
            subprocess.call(['i2cdetect', '-y', '1'])
            print(err)

    def highlightDrink(self, recipe):
        jars = [str(ing.get("jar_pos")) for ing in recipe if ing.get("jar_pos") != None]
        jarString = ','.join(jars)

        cmd = "show:{}".format(jarString)
        self.writeBlock(cmd)

    def getSizeFactor(self):
        # get drink sizes
        if(GPIO.input(self.spin) == GPIO.HIGH):
            return 1 #single

        if(GPIO.input(self.dpin) == GPIO.HIGH):
            return 2 #double

        return 0.25 #sample


    def dispenseDrink(self, recipe):
        size = self.getSizeFactor()

        print("Dispensing recipe...")
        for ing in recipe:
            print(ing)
            if(ing.get("jar_pos") is not None and ing.get("oz") is not None):
                msPerOz = self.msPerOz if ing.get("flow") is None else ing.get("flow")
                t = abs(ing["oz"] * msPerOz * size)

                prime = int(self.prime.get(str(ing["jar_pos"]), 0))
                t += abs(prime)

                cmd = "pump:%d:%d" % (ing["jar_pos"], t)
                self.writeBlock(cmd)

                time.sleep(t / 1000) #I think this will block the rest of the code so a user can't double select.
                print("what im done")