from RPi import GPIO
from time import sleep, time

# State table code adapted from https://github.com/buxtronix/arduino/tree/master/libraries/Rotary
R_START = 0x0
R_CW_FINAL = 0x1
R_CW_BEGIN = 0x2
R_CW_NEXT = 0x3
R_CCW_BEGIN = 0x4
R_CCW_FINAL = 0x5
R_CCW_NEXT = 0x6

# Values returned by 'process'
# No complete step yet.
DIR_NONE = 0x0
# Clockwise step.
DIR_CW = 0x10
# Anti-clockwise step.
DIR_CCW = 0x20

ttable = [
  # R_START
  [R_START,    R_CW_BEGIN,  R_CCW_BEGIN, R_START],
  # R_CW_FINAL
  [R_CW_NEXT,  R_START,     R_CW_FINAL,  R_START | DIR_CW],
  # R_CW_BEGIN
  [R_CW_NEXT,  R_CW_BEGIN,  R_START,     R_START],
  # R_CW_NEXT
  [R_CW_NEXT,  R_CW_BEGIN,  R_CW_FINAL,  R_START],
  # R_CCW_BEGIN
  [R_CCW_NEXT, R_START,     R_CCW_BEGIN, R_START],
  # R_CCW_FINAL
  [R_CCW_NEXT, R_CCW_FINAL, R_START,     R_START | DIR_CCW],
  # R_CCW_NEXT
  [R_CCW_NEXT, R_CCW_FINAL, R_CCW_BEGIN, R_START],
]

class EncoderInput:

    bounce = 2
    dtDetect = False
    state = R_START
    # btnInProgress = False

    def __init__(self, clk, dt, btn, rled, gled, bled):
        self.clk = clk
        self.dt = dt
        self.btn = btn

        self.rled = rled
        self.gled = gled
        self.bled = bled

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clk, GPIO.IN)
        GPIO.setup(self.dt, GPIO.IN)
        GPIO.setup(self.btn, GPIO.IN)

        GPIO.setup(self.rled, GPIO.OUT)
        GPIO.setup(self.gled, GPIO.OUT)
        GPIO.setup(self.bled, GPIO.OUT)

        self.setColor(0, 0, 1)

    def setupEncoderEvents(self, turnCallback, btnCallback):
        self.turnCallback = turnCallback
        self.btnCallback = btnCallback

        #event for turning dial
        GPIO.add_event_detect(self.clk, GPIO.BOTH, callback=self.handleEncoder, bouncetime=self.bounce)
        GPIO.add_event_detect(self.dt, GPIO.BOTH, callback=self.handleEncoder)

        #event for clicking button
        GPIO.add_event_detect(self.btn, GPIO.RISING, callback=self.handleEncoderPress, bouncetime=1000)
        # GPIO.add_event_callback(self.btn, lambda channel: print("HEY STEVE"))

    def sampleChannel(self, channel, sampleTime):
        now = time()
        list = []     #Stores IO samples from encoder dt. (or whatever)

        while time() <= now + sampleTime: #Get samples over 2mS period of IO 'dt' state; as many as possible
            list = list + [GPIO.input(channel)]

        return int(round(sum(list) / len(list)))

    def setColor(self, r, g, b):
        GPIO.output(self.rled, r)
        GPIO.output(self.gled, g)
        GPIO.output(self.bled, b)

    def handleEncoderPress(self, channel):
        state = self.sampleChannel(self.btn, 0.010) #sample 10 ms

        if state:
            print("------encoder button callback begin---------")
            self.setColor(1, 0, 0)
            self.btnCallback()
            self.setColor(0, 1, 0)
            sleep(2) # wait 2 seconds before accepting more input
            self.setColor(0, 0, 1)
        else:
            print("----------BUTTON PRESS IGNORED!-------------")

    def rotaryState(self):
        # Grab state of input pins.
        pinstate = (GPIO.input(self.clk) << 1) | GPIO.input(self.dt)
        # Determine new state from the pins and state table.
        self.state = ttable[self.state & 0xf][pinstate]
        # Return emit bits, ie the generated event.
        return self.state & 0x30

    def handleEncoder(self, channel): # channel is not used, but is required to handle the event.
        result = self.rotaryState()

        if result == DIR_CW:
            self.turnCallback(1)
            # counter++;
            # Serial.println(counter);
        elif result == DIR_CCW:
            self.turnCallback(-1)
            # counter--;
            # Serial.println(counter);