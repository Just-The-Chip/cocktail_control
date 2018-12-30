from RPi import GPIO
from time import sleep, time
from collections import deque

class EncoderInput:

    # btnInProgress = False

    #Sample count, storage and timing variables for rotation sampling:
    samplesPerMs = 40                                           #How many encoder samples to capture per millisecond.
    sampleTime = 0.00025                                        #Samples time in seconds.
    sampleDwell = 0.001 / samplesPerMs                          #Wait time between samples to free up processor for other things.
    sampleBufferSize = int(samplesPerMs * (sampleTime * 1000))  #Size of the sample buffer for each encoder channel.
    samplesB = deque([True]*sampleBufferSize, sampleBufferSize) #Buffer that stores [sampleBufferSize] number of samples from encoder channel B.
    samplesA = deque([True]*sampleBufferSize, sampleBufferSize) #Buffer that stores [sampleBufferSize] number of samples from encoder channel A.
    lastSampleTime = time()                                     #Last time encoder channels were sampled.  Used for sample timing.
    stateTime = time()                                          #Contains the last time the state was changed.

    #Counter UI visual variables: (for troubleshooting only)
    #counterString = ""                                         #Serves as a visual representation of rotary input.

    def __init__(self, EnB, EnA, btn, rled, gled, bled):
        self.EnA = EnA
        self.EnB = EnB
        self.btn = btn

        self.rled = rled
        self.gled = gled
        self.bled = bled

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.EnA, GPIO.IN)
        GPIO.setup(self.EnB, GPIO.IN)
        GPIO.setup(self.btn, GPIO.IN)

        GPIO.setup(self.rled, GPIO.OUT)
        GPIO.setup(self.gled, GPIO.OUT)
        GPIO.setup(self.bled, GPIO.OUT)

        self.setColor(0, 0, 1)

    def setupEncoderEvents(self, turnCallback, btnCallback):
        self.turnCallback = turnCallback
        self.btnCallback = btnCallback

        #event for turning dial
        GPIO.add_event_detect(self.EnA, GPIO.FALLING, callback=self.handleEncoder)#, bouncetime=1)
        GPIO.add_event_detect(self.EnB, GPIO.FALLING, callback=self.handleEncoder)#, bouncetime=1)

        #event for clicking button
        GPIO.add_event_detect(self.btn, GPIO.RISING, callback=self.handleEncoderPress, bouncetime=1000)
        # GPIO.add_event_callback(self.btn, lambda channel: #print("HEY STEVE"))

    def sampleChannel(self, channel, sampleTime):
        now = time()
        list = []     #Stores IO samples from encoder EnB. (or whatever)

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
            #print("------encoder button callback begin---------")
            self.setColor(1, 0, 0)
            self.btnCallback()
            self.setColor(0, 1, 0)
            sleep(2) # wait 2 seconds before accepting more input
            self.setColor(0, 0, 1)
        else:
            pass
            #print("----------BUTTON PRESS IGNORED!-------------")

    def handleEncoder(self, channel): # channel is not used, but is required to handle the event.

        #Encoder state and timing variables:
        stateB = True                   #State of encoder channel B (filtered). Logic is made to match that of the encoder.
        stateA = True                   #State of encoder channel A (filtered). Logic is made to match that of the encoder.
        bFirst = False                  #Indicates if encoder channels B went low first.
        encoderState = 0                #States: Idle, One channel low, Both channels low, One channel back high, Both channels back high (0, 1, 2, 3, 4 respectively)

        if time() <= (self.stateTime + 0.0015):  #Adds debounce and Prevents callbacks that queued up during rotation from executing.
            #print("pass")
            return

        # if channel == 17:                         #For Troubleshooting
        #     print("Channel A ", end="")
        # else:
        #     print("Channel B ", end="")
        #print(encoderState, end="")

        def stateChange(stateNumber):               #Updates state machine state and updates time of the change.
            nonlocal encoderState

            # if encoderState == 4:                 #This IF is for troubleshooting
            #     #print("E")
            #     pass
            # else:
            #     print(stateNumber, end="")
        
            encoderState = stateNumber
            self.stateTime = time()


        triggerTime = time()                    #Time that the callbackw as triggered.

        while True:                             #This is the state machine.
            ############################ SAMPLE CHANNELS ############################
            #This first block alwayse executes.
            #It takes samples and updates the encoder channels filtered values every time it executes.
            #Advances state machine when either encoder channels buffer reads all false.
            if time() >= self.lastSampleTime + self.sampleDwell:      #This 'if' samples both encoder channels 'samplesPerMs' times a millisecond.
                self.lastSampleTime = time()
                self.samplesB.append(GPIO.input(self.EnB))
                self.samplesA.append(GPIO.input(self.EnA))
                if all(self.samplesB):                     #Updates 'stateB' continously
                    stateB = True
                if all(self.samplesA):                     #Updates 'stateA' continously
                    stateA = True
                if not any(self.samplesB):                 #Updates 'stateB' continously, tracks channels firstness, and advances state
                    stateB = False
                    if encoderState == 0 and stateA:
                        bFirst = True
                        stateChange(1)
                if not any(self.samplesA):                 #Updates 'stateA' continously, tracks channels firstness, and advances state
                    stateA = False
                    if encoderState == 0 and stateB:
                        bFirst = False
                        stateChange(1)
            ############################ State 0 - Idle: ############################
            #Exits callback if [time] elapses.
            if encoderState == 0:
                if time() >= (triggerTime + 0.003):
                    stateChange(0)
                    #print("Break")
                    break
            
            ############################ State 1 - One channel low: ############################
            #Resets state machine if timeout elapses. Goes back to previous state if the encoder channel that went low first goes high again.
            #Advances state machine if both encoder channels filtered logic are low at the same time.
            if encoderState == 1:
                if time() >= (self.stateTime + 0.200):      #Timeout Reset (seconds)
                    stateChange(0)
                    #print(" case1 B")
                    break
                elif bFirst and stateB:                     #Unexpected channel B Reset
                    stateChange(0)
                    #print(" case2 B")
                    break
                elif not bFirst and stateA:                 #Unexpected channel A Reset
                    stateChange(0)
                    #print(" case3 B")
                    break
                elif not stateB and not stateA:             #Advance state machine 
                    stateChange(2)
            
            ############################ State 2 - Both channels low: ############################
            #Resets state machine if timeout elapses. Goes back to previous state if wrong encoder channel goes high first.
            #Advances state machine if the correct channel goes high.
            if encoderState == 2:
                if time() >= (self.stateTime + 0.110):      #Timeout Reset (seconds)
                    stateChange(0)
                    #print(" case1 B", time() - triggerTime)
                    break
                elif stateA and stateB:                     #Unexpected both channels go back high. Not sure why this happens, but skipping to state 4 improves recognition.
                    #print(" case2 ", time() - self.stateTime, end=" ")
                    stateChange(4)
                elif bFirst and stateA:                     #Unexpected channel Reset A
                    #print(" case5 ", time() - self.stateTime, end=" ")
                    stateChange(1)
                    #encoderState = 1
                elif not bFirst and stateB:                 #Unexpected channel Reset B
                    #print(" case6 ", time() - self.stateTime, end=" ")
                    stateChange(1)
                    #encoderState = 1
                elif bFirst and stateB:                     #Advance state, expected channel B
                    stateChange(3)
                elif not bFirst and stateA:                 #Advance state, expected channel A
                    stateChange(3)
            
            ############################ State 3 - One channel back high: ############################
            #Resets state machine if timeout elapses. Goes back to previous state if encoder channel that just went high goes low again.
            #Advances state machine if a single sample reads high in the expected encoder channels buffer.
            if encoderState == 3:
                if time() >= (self.stateTime + 0.040):      #Timeout Reset (seconds)
                    stateChange(0)
                    #print(" case1 B")
                    break
                    #print("State 3 timeout")
                elif bFirst and not stateB:                 #Unexpected channel Reset B
                    stateChange(2)
                    #encoderState = 2
                elif not bFirst and not stateA:             #Unexpected channel ResetA
                    stateChange(2)
                    #encoderState = 2
                elif bFirst and any(self.samplesA):         #Advance state, expected channel A
                    stateChange(4)
                elif not bFirst and any(self.samplesB):     #Advance state, expected channel B
                    stateChange(4)
            
            ############################ State 4 - Both channels back high ############################
            #Resets state machine upon completion of this block.
            #Updates rotation visual.
            if encoderState == 4:
                if bFirst:                                  #Counter ClockWise visual
                    self.turnCallback(-1)
                    #self.counterString = self.counterString[0:len(self.counterString)-1]
                    #print(self.counterString)
                    #print("CCW")
                else:                                       #ClockWise visual
                    self.turnCallback(1)
                    #self.counterString = self.counterString + "-"
                    #print(self.counterString)
                    #print("CW")
                stateChange(0)
                break
