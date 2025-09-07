import asyncio
import app
import time
import asyncio
import math

from events.input import Buttons, BUTTON_TYPES
from app_components import clear_background
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable

class TildularSequencer(app.App):

    beatInterval = 0.5 #seconds
    beat = 0
    numBeats = 4
    maxBeats = 6
    sweepPos = 0.0 # float, goes from 0 to numBeats as time goes by
    fractionOfBeat = 0

    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)
        # This disables the patterndisplay system module, which does the
        # default colour spinny thing
        eventbus.emit(PatternDisable())
        tildagonos.set_led_power(True)

    def update(self, delta):

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

        self.sweepPos = self.sweepPos + (0.001*delta)/self.beatInterval
        if self.sweepPos > self.numBeats:
            self.sweepPos = self.sweepPos - self.numBeats

        self.beat = math.floor(self.sweepPos)
        
        self.fractionOfBeat = self.sweepPos % 1.0

        self.updateLEDs()

        return True
    

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
        clear_background(ctx)

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
        bigBlobSize = 20
        smallBlobSize = 10
        dotSize = 2

        for b in range(0,self.maxBeats):
            r = 255
            if b == self.beat:
                #fill
                size = self.fmap(self.fractionOfBeat, 0.0, 1.0, bigBlobSize, smallBlobSize)
                r = int(self.fmap(self.fractionOfBeat, 0.0, 1.0, 0, 255))
                fill = True
            elif b < self.numBeats:
                #empty
                size = smallBlobSize
                fill = False
            else:
                #dot
                size = dotSize
                fill = False

            theta = self.thetaForBeat(b)

            x = blobRadius*math.cos(theta)
            y = blobRadius*math.sin(theta)
            if fill:
                ctx.rgb(r, 234, 0).arc(x,y, size, 0, 2 * math.pi, True).fill()
            else:
                ctx.rgb(r, 234, 0).arc(x,y, size, 0, 2 * math.pi, True).stroke()

        #crosshairs
        #ctx.rgb(0, 1, 0).begin_path()
        #ctx.move_to(-120, 0)
        #ctx.line_to(120, 0)
        #ctx.move_to(0, 120)
        #ctx.line_to(0, -120)
        #ctx.stroke()

        ctx.restore()

        


__app_export__ = TildularSequencer