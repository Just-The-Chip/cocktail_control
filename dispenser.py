#I2C Pins
#GPIO2 -> SDA
#GPIO3 -> SCL
# pump:jarpos:ms
# flush

from RPi import GPIO
import smbus
import time
import subprocess
import crc16

class Dispenser:

    def __init__(self, address, **kwargs):
        self.address = address
        # self.msPerOz = kwargs.get('mspoz', 1000)
        self.prime = kwargs.get('prime', {})

        self.bus = smbus.SMBus(1) # for RPI version 1, use "bus = smbus.SMBufs(0)"
        self.spin = kwargs.get('spin', 10)
        self.dpin = kwargs.get('dpin', 11)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.spin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def writeBlock(self, byteCmd):  #This sends the command.  First byte sent is the number of characters in the command.

        crc = self.calcCRC(byteCmd)
        value = list(byteCmd + crc.to_bytes(2, 'big'))

        try:
            self.bus.write_i2c_block_data(self.address, len(value), value)
            return -1
        except OSError as err:
            subprocess.call(['i2cdetect', '-y', '1'])
            print(err)

    def startCmd(self, numIngredients):
        return b'p' + numIngredients.to_bytes(1, 'big')
        # cmd = "pump:%d:" % (numIngredients)

    def ingredientCmd(self, jar_pos, amount): # amount is in miligrams
        return jar_pos.to_bytes(1, 'big') + amount.to_bytes(4, 'big')
        # cmd = "ing:%d:%d:" % (jar_pos, amount)

    def calcCRC(self, byteCmd):
        return crc16.crc16xmodem(byteCmd)

    def highlightDrink(self, recipe):
        jars = [str(ing.get("jar_pos")) for ing in recipe if ing.get("jar_pos") != None]
        jarString = ','.join(jars)

        cmd = "show:{}".format(jarString)
        self.writeBlock(cmd)

    def getSizeFactor(self):
        # get drink sizes
        if(GPIO.input(self.spin) == GPIO.LOW):
            return 1 #single

        if(GPIO.input(self.dpin) == GPIO.LOW):
            return 2 #double

        return 0.25 #sample


    def dispenseDrink(self, recipe):
        mgPerOz = 28349.5
        size = self.getSizeFactor()

        # start cmd sends number of ingredients
        self.writeBlock(self.startCmd(len*recipe.get("ing")))

        print("Dispensing recipe...")
        for ing in recipe:
            print(ing)
            if(ing.get("jar_pos") is not None and ing.get("oz") is not None):

                mg = abs(ing["oz"] * mgPerOz * size)

                # next comands simply send jar position and number of mg
                cmd = self.ingredientCmd(ing.get("jar_pos"), mg)
                self.writeBlock(cmd)

                # time.sleep(t / 1000) #I think this will block the rest of the code so a user can't double select.
                print("what im done")