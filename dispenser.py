#I2C Pins 
#GPIO2 -> SDA
#GPIO3 -> SCL
# pump:jarpos:ms
# flush

import smbus
import time

class Dispenser:

    def __init__(self, address, **kwargs):
        self.address = address
        self.msPerOz = kwargs.get('mspoz', 1000)
        self.bus = smbus.SMBus(1) # for RPI version 1, use "bus = smbus.SMBus(0)"

    def writeBlock(self, string):  #This sends the command.  First byte sent is the number of characters in the command.
        value = list(map(ord, string))

        try:
            self.bus.write_i2c_block_data(self.address, len(value), value)
            return -1
        except OSError as err:
            print(err)

    def dispenseDrink(self, recipe):
        for ing in recipe:
            print(ing)
            if(ing.get("jar_pos") != None and ing.get("oz") != None):
                t = ing["oz"] * self.msPerOz
                cmd = "pump:%d:%d" % (ing["jar_pos"], t)
                self.writeBlock(cmd)
                time.sleep(t / 1000) #I think this will block the rest of the code so a user can't double select.