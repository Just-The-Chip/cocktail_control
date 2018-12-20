from RPi import GPIO
from time import sleep, time
import atexit


rled = 23
gled = 24
bled = 18
leds = (rled, gled, bled)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(leds, GPIO.OUT)

# GPIO.setup(rled, GPIO.OUT)
# GPIO.setup(gled, GPIO.OUT)
# GPIO.setup(bled, GPIO.OUT)

GPIO.output(leds, (0,0,0))

def cleanup():
    # GPIO.output(rled, 0)
    # GPIO.output(gled, 0)
    # GPIO.output(bled, 1)
    GPIO.output(leds, (0,0,0))
    GPIO.cleanup()

atexit.register(cleanup)


while True:
    # GPIO.output(rled, 1)
    GPIO.output(leds, (1,0,0))
    print("red on")
    sleep(1)
    # GPIO.output(rled, 0)
    # GPIO.output(gled, 1)
    GPIO.output(leds, (0,1,0))
    print("green on")
    sleep(1)
    # GPIO.output(gled, 0)
    # GPIO.output(bled, 1)
    GPIO.output(leds, (0,0,1))
    print("blue on")
    sleep(1)
    # GPIO.output(bled, 0)