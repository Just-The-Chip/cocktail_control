from RPi import GPIO
from time import sleep, time

class EncoderInput:

    bounce = 50
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
        GPIO.add_event_detect(self.clk, GPIO.FALLING, callback=self.handleEncoder, bouncetime=self.bounce)
        #GPIO.add_event_callback(self.clk, lambda channel: print("RECEIVED NEXT WIDGET COMMAND"))

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

    def handleEncoder(self, channel): # channel is not used, but is required to handle the event.
        state = self.sampleChannel(self.dt, 0.002)

        if state: #If dt state is True, encoder is turning Counter Clockwise, pass -1 to callback
            self.turnCallback(-1)
        else:     #else, encoder is turning Clockwise, pass 1 to callback
            self.turnCallback(1)