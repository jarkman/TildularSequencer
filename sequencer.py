import asyncio
import app
import time
import asyncio
import math


from events.input import Buttons, BUTTON_TYPES
from events.joystick import JOYSTICK_BUTTON_TYPES
from app_components import clear_background
from .sequencerHexpansion import DACSlots, ADCSlots
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
from frontboards.twentysix import TwentyTwentySix 

#import sequencerHexpansion

class Sequencer():

    beatInterval = 0.5 #seconds
    beat = 0
    numBeats = 4
    maxBeats = 12
    sweepPos = 0.0 # float, goes from 0 to numBeats as time goes by
    fractionOfBeat = 0

    def __init__(self, app, sequencerHexpansion, channel, buttonStates, envelope, quantiser):
        super().__init__()
        self.app = app
        self.sequencerHexpansion = sequencerHexpansion
        self.channel = channel
        self.buttonStates = buttonStates
        self.envelope = envelope
        self.quantiser = quantiser
        self.selectedNote = -1
        self.notes = []
        for n in range(self.maxBeats):
            self.notes.append(1.0+ n/self.maxBeats) # initialise with an arpeggio

        if self.channel == 1:
            self.DACSlot = DACSlots.CV1
            self.GateSlot = DACSlots.Gate1
        else:
            self.DACSlot = DACSlots.CV2
            self.GateSlot = DACSlots.Gate2
        
    def buttonDownHandler(self, event):
        #print("sequencer button event " + repr(event))

        if JOYSTICK_BUTTON_TYPES["LEFT"] in event.button:
            self.numBeats = max(self.numBeats-1, 0)
        if JOYSTICK_BUTTON_TYPES["RIGHT"] in event.button:
            self.numBeats = min(self.numBeats+1, self.maxBeats)


    def update(self, delta):
        #self.updateLEDs()

        #self.background_update(delta)

        #print(repr(self.buttonStates))
        self.selectedNote = -1

        for i in range(12):
            touchN = i+1 # count 1-12
            
            key = "TOUCH%02d" % (touchN)

            if TwentyTwentySix.touch_states[key][0] and i < self.numBeats:
                self.selectedNote = i

        

        
        for i in range(0, 12):
            if i < self.numBeats:
                tildagonos.leds[i+1] = (0, 255, 0) # light up active ones green
            else:
                tildagonos.leds[i+1] = (0, 0, 0)

        if self.selectedNote > -1:
            tildagonos.leds[self.selectedNote*2+1] = (0, 0, 255) # selected one is blue

            # update CV vaue from knob
            volts = self.sequencerHexpansion.adc[ADCSlots.Pitch][1]
            #print("new note volts " + repr(volts))
            self.notes[self.selectedNote] = volts
            
            
        tildagonos.leds.write()

        return True
    
        
    def background_update(self, delta):

        #print("sequencer backgroundUpdate ch "+ repr(self.channel) + " delta " + repr(delta))

        oldF = self.fractionOfBeat

        self.fractionOfBeat = self.app.clock.fractionOfBeat

        if oldF > self.fractionOfBeat:
            # a new beat has to happen
            self.beat = (self.beat + 1) % self.numBeats
            if self.notes[self.beat] > 0.0:
                # emit new note
                #print("new note4 " + repr(self.notes[newBeat])+ " V")
                volts = self.notes[self.beat]
                volts = self.quantiser.quantise(volts)
                self.sequencerHexpansion.writeCV(self.DACSlot, volts)
                self.envelope.startEnvelope()
                #self.sequencerHexpansion.startPulse(self.GateSlot)

        self.sweepPos = self.beat + self.fractionOfBeat
       

    def updateLEDs(self):

        for beat in range(0, self.maxBeats):
            r = 0
            g = 255
            b = 0
            if beat == self.beat:
                r = 255
            for l in range(0, 2):
                tildagonos.leds[beat*2+l] = (r,g,b)
                
        tildagonos.leds.write()

        

        


    def thetaForBeat(self, b):
        theta = 2.0*math.pi*b/self.maxBeats
        theta = theta - math.pi/2.0 # put 0 at the top
        return theta
    
    def fmap(self, f, fMin, fMax, oMin, oMax):
        return( oMin + (oMax-oMin)*(f-fMin)/(fMax-fMin))
    
    def draw(self, ctx):
        
        ctx.save()

        ctx.font_size = self.app.fontSize

        #ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
        #ctx.rgb(1,0,0).move_to(-80,0).text("T" + repr(self.totalT))
        
        # clock hand
        ctx.rgb(0, 1, 0).begin_path()
        
        clockOuterRadius = 90
        clockInnerRadius = 50
        
        theta = self.thetaForBeat(self.sweepPos)

        x0 = clockInnerRadius*math.cos(theta)
        y0 = clockInnerRadius*math.sin(theta)
        x1 = clockOuterRadius*math.cos(theta)
        y1 = clockOuterRadius*math.sin(theta)
        ctx.move_to(x0,y0)
        ctx.line_to(x1,y1)
        ctx.stroke()

        blobRadius = 110
        if self.selectedNote >= 0:
            bigBlobSize = 50
        else:
            bigBlobSize = 35

        dotSize = 2

        for beat in range(0,self.maxBeats):
            r = 255
            if beat == self.selectedNote:
                #fill
                size = self.fmap(self.fractionOfBeat, 0.0, 1.0, bigBlobSize*2.0, bigBlobSize*2.0/2.0)
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                g = 234
                b = 0
                fill = True
            elif beat == self.beat:
                #fill
                size = self.fmap(self.fractionOfBeat, 0.0, 1.0, bigBlobSize, bigBlobSize/2.0)
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                g = 234
                b = 0
                fill = True
            elif beat < self.numBeats:
                #empty
                size = bigBlobSize/2.0
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                g = 234
                b = 0
                fill = True
            else:
                #dot
                size = dotSize
                r = 0
                g = 0
                b = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                fill = False

            if beat < self.numBeats:
                fraction = self.notes[beat]/self.sequencerHexpansion.maxVolts
                if fraction < 0.001:
                    fill = False # show non-playing notes as empty
            else:
                fraction = 0

            

            theta = self.thetaForBeat(beat)

            x = blobRadius*math.cos(theta)
            y = blobRadius*math.sin(theta)
            if fill:
                
                ctx.rgb(r, g, b).arc(x,y, size+2, 0, 2 * math.pi, True).fill()
                ctx.rgb(r,0,0).arc(x,y, size*fraction, 0, 2 * math.pi, True).fill() # and an inner circle to show volts
            else:
                ctx.rgb(r,g,b).arc(x,y, size, 0, 2 * math.pi, True).stroke()

        ctx.text_align = ctx.CENTER
        ctx.gray(1)
        ctx.move_to(0,0).text("Sequencer")
        ctx.move_to(0,20).text("Ch " + repr(self.channel))
        
        ctx.move_to(0,80).text("<- %d +>"%(self.numBeats))

        ctx.restore()

        
