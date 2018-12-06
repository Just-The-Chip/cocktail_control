from RPi import GPIO
from time import sleep, time
import atexit

leds = (4, 5, 6)
rled = 4
gled = 5
bled = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(leds, GPIO.OUT)
GPIO.output(leds, (1,1,1))
# GPIO.setup(rled, GPIO.OUT)
# GPIO.setup(gled, GPIO.OUT)
# GPIO.setup(bled, GPIO.OUT)


while True:
    # GPIO.output(rled, 0)
    GPIO.output(leds, (0,1,1))
    sleep(1)
    # GPIO.output(rled, 1)
    # GPIO.output(gled, 0)
    GPIO.output(leds, (1, 0, 1))
    sleep(1)
    # GPIO.output(gled, 1)
    # GPIO.output(bled, 0)
    GPIO.output(leds, (1, 1, 0))
    sleep(1)
    # GPIO.output(bled, 1)

def cleanup():
    # GPIO.output(rled, 1)
    # GPIO.output(gled, 1)
    # GPIO.output(bled, 1)
    GPIO.output(leds, (1,1,1))
    GPIO.cleanup()

atexit.register(cleanup)