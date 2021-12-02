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

class ReadTimeoutError(Exception): 
    pass
class Dispenser:

    def __init__(self, address, **kwargs):
        self.address = address

        # self.msPerOz = kwargs.get('mspoz', 1000)
        # self.prime = kwargs.get('prime', {})

        self.bus = smbus.SMBus(1) # for RPI version 1, use "bus = smbus.SMBufs(0)"
        self.spin = kwargs.get('spin', 10)
        self.dpin = kwargs.get('dpin', 11)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.spin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def writeBlock(self, byteCmd):  #This sends the command.  First byte sent is the number of characters in the command.

        crc = self.calcCRC(byteCmd)
        print("CRC: ")
        print(crc)
        value = list(byteCmd + crc.to_bytes(2, 'big'))

        print("sending command: ")
        print(value)

        hexval = map(hex, value)
        print(list(hexval))

        maxResends = 5
        resends = 0
        writeSuccess = False
        try:
            print("attempting write...")
            while not writeSuccess and resends < maxResends:
                print("resend #" + str(resends))
                self.bus.write_i2c_block_data(self.address, len(value), value)
                time.sleep(5)
                writeSuccess = self.sendAcknowledged()
                resends += 1

            return writeSuccess
        except ReadTimeoutError as err:
            print(err)
        except OSError as err:
            print("OS ERROR oh no")
            subprocess.call(['i2cdetect', '-y', '1'])
            print(err)

        return False

    def sendAcknowledged(self):
        maxRetries = 50
        retryCount = 0
        responseVal = 0

        print("=(^. .^)= BEGINNING SEND ACKNOLEGEMENT")

        # print("lol jk, just mocking the return...")
        # return True

        while retryCount < maxRetries:
            print("try #" + str(retryCount))
            responseVal = self.bus.read_i2c_block_data(self.address, 21, 1)
            if responseVal[0] == 6: # ASCII for ACK
                print("ACK RECIEVED")
                return True
            elif responseVal[0] == 21: # ASCII for NAK
                print("NACK RECIEVED")
                return False

            print("Didn't get anything, retrying.")
            retryCount += 1
            time.sleep(0.1)

        raise ReadTimeoutError

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

        print(recipe)
        print("size: " + str(size))

        # start cmd sends number of ingredients
        self.writeBlock(self.startCmd(len(recipe)))

        print("Dispensing recipe...")
        for ing in recipe:
            print(ing)
            time.sleep(5)
            if(ing.get("jar_pos") is not None and ing.get("oz") is not None):

                mg = abs(ing["oz"] * mgPerOz * size)

                print("mg: " + str(round(mg)))

                # next comands simply send jar position and number of mg
                cmd = self.ingredientCmd(ing.get("jar_pos"), round(mg))
                self.writeBlock(cmd)

                # todo: accept ack or handle nack

                # time.sleep(t / 1000) #I think this will block the rest of the code so a user can't double select.
                print("what im done")