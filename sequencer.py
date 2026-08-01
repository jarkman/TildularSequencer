import asyncio
import app
import time
import asyncio
import math

from events.input import Buttons, BUTTON_TYPES
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
    maxBeats = 6
    sweepPos = 0.0 # float, goes from 0 to numBeats as time goes by
    fractionOfBeat = 0

    def __init__(self, app, sequencerHexpansion, channel, buttonStates):
        super().__init__()
        self.app = app
        self.sequencerHexpansion = sequencerHexpansion
        self.channel = channel
        self.buttonStates = buttonStates
        self.selectedNote = -1
        self.notes = []
        for n in range(self.maxBeats):
            self.notes.append((3.3 * n)/self.maxBeats) # initialise with an arpeggio

        if self.channel == 1:
            self.DACSlot = DACSlots.CV1
            self.GateSlot = DACSlots.Gate1
        else:
            self.DACSlot = DACSlots.CV2
            self.GateSlot = DACSlots.Gate2
        

    def update(self, delta):
        #self.updateLEDs()

        #self.background_update(delta)

        #print(repr(self.buttonStates))

        if TwentyTwentySix.touch_states["TOUCH01"][0]:
            self.selectedNote = 0
        elif TwentyTwentySix.touch_states["TOUCH03"][0]:
            self.selectedNote = 1
        elif TwentyTwentySix.touch_states["TOUCH05"][0]:
            self.selectedNote = 2
        elif TwentyTwentySix.touch_states["TOUCH07"][0]:
            self.selectedNote = 3
        elif TwentyTwentySix.touch_states["TOUCH09"][0]:
            self.selectedNote = 4
        elif TwentyTwentySix.touch_states["TOUCH11"][0]:
            self.selectedNote = 5
        else:
            self.selectedNote = -1        

        # only use odd-numbered LEDs
        for i in range(0, 12):
            if i%2 == 0:
                tildagonos.leds[i+1] = (0, 255, 0) # light up active ones green
            else:
                tildagonos.leds[i+1] = (0, 0, 0)

        if self.selectedNote > -1:
            tildagonos.leds[self.selectedNote*2+1] = (0, 0, 255) # selected one is blue

            # update CV vaue from knob
            volts = self.sequencerHexpansion.adc[ADCSlots.Pitch][1]
            print("new note volts " + repr(volts))
            self.notes[self.selectedNote] = volts
            
            
        tildagonos.leds.write()

        return True
    
        
    def background_update(self, delta):

        print("sequencer backgroundUpdate ch "+ repr(self.channel) + " delta " + repr(delta))

        self.sweepPos = self.sweepPos + (0.001*delta)/self.beatInterval
        if self.sweepPos > self.numBeats:
            self.sweepPos = self.sweepPos - self.numBeats

        newBeat = math.floor(self.sweepPos)

        if newBeat != self.beat:
            if self.notes[newBeat] > 0.0:
                # emit new note
                #print("new note4 " + repr(self.notes[newBeat])+ " V")
                self.sequencerHexpansion.writeCV(self.DACSlot, self.notes[newBeat])
                self.sequencerHexpansion.startPulse(self.GateSlot)

            
        self.beat = newBeat
        
        self.fractionOfBeat = self.sweepPos % 1.0

       

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
            bigBlobSize = 20

        dotSize = 2

        for b in range(0,self.maxBeats):
            r = 255
            if b == self.selectedNote:
                #fill
                size = self.fmap(self.fractionOfBeat, 0.0, 1.0, bigBlobSize*2.0, bigBlobSize*2.0/2.0)
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                fill = True
            elif b == self.beat:
                #fill
                size = self.fmap(self.fractionOfBeat, 0.0, 1.0, bigBlobSize, bigBlobSize/2.0)
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                fill = True
            elif b < self.numBeats:
                #empty
                size = bigBlobSize/2.0
                fill = True
            else:
                #dot
                size = dotSize
                fill = False

            if b < self.numBeats:
                fraction = self.notes[b]/self.sequencerHexpansion.maxVolts
                if fraction < 0.001:
                    fill = False # show non-playing notes as empty
            else:
                fraction = 0

            theta = self.thetaForBeat(b)

            x = blobRadius*math.cos(theta)
            y = blobRadius*math.sin(theta)
            if fill:
                divider = fraction * 2 * math.pi
                ctx.rgb(r, 234, 0).arc(x,y, size, 0, 2 * math.pi, True).fill()
                ctx.rgb(0, 234, r).arc(x,y, size*fraction, 0, 2 * math.pi, True).fill()
            else:
                ctx.rgb(0, 0, r).arc(x,y, size, 0, 2 * math.pi, True).stroke()

        #crosshairs
        #ctx.rgb(0, 1, 0).begin_path()
        #ctx.move_to(-120, 0)
        #ctx.line_to(120, 0)
        #ctx.move_to(0, 120)
        #ctx.line_to(0, -120)
        #ctx.stroke()

        ctx.restore()

        
