import asyncio
import app
import time
import asyncio
import math


from events.input import Buttons, BUTTON_TYPES
from events.joystick import JOYSTICK_BUTTON_TYPES
from app_components import clear_background
from .sequencerHexpansion import DACSlots, ADCSlots, MAX_VOLTS
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
from frontboards.twentysix import TwentyTwentySix, TOUCH 
import imu

def fmap(f, fMin, fMax, oMin, oMax):
    return( oMin + (oMax-oMin)*(f-fMin)/(fMax-fMin))

class Tilt():

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
        self.selectedNote = 0
        self.octave = 0
        self.dirLabel = "---"

        self.acc_read = None

        if self.channel == 1:
            self.DACSlot = DACSlots.CV1
            self.GateSlot = DACSlots.Gate1
            self.dirLabel = "V ^"
        else:
            self.DACSlot = DACSlots.CV2
            self.GateSlot = DACSlots.Gate2
            self.dirLabel = "< >"
        
    def buttonDownHandler(self, event):

        return

        
    def update(self, delta):
        
        
        
        #for i in range(0, 12):
        #    tildagonos.leds[i+1] = (0, 0, 255)

        #tildagonos.leds[self.selectedNote+1] = (0,255,0) 
        #tildagonos.leds.write()

        return True
    
        
    def background_update(self, delta):

        self.acc_read = imu.acc_read()

        g = 0

        if self.channel == 1:
            g = self.acc_read[0]
            
        if self.channel == 2:
            g = self.acc_read[1]
            

        volts = fmap(g, -9.81, 9.81, 0, MAX_VOLTS)

        self.sequencerHexpansion.writeCV(self.DACSlot, volts)
        self.sequencerHexpansion.writeCV(self.GateSlot, MAX_VOLTS)


        return
    
        
       

    

    
    def draw(self, ctx):
        

        ctx.save()


        #ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        #if self.acc_read:
        #    ctx.rgb(1, 0, 0).move_to(-80, -40).text(
        #        "accel x,y,z:\n{},\n{},\n{}".format(
        #            self.acc_read[0], self.acc_read[1], self.acc_read[2]))
        #else:
        #    ctx.rgb(1, 0, 0).move_to(-80, 0).text("no readings yet")


        ctx.rgb(1,0,0).move_to(-30,-20).text("Tilt")
        
        ctx.rgb(1,0,0).move_to(-10,0).text("Ch " + repr(self.channel) + " " + self.dirLabel)
        
        ctx.rgb(1,0,0).move_to(-30,20).text("Octave " + repr(self.octave))

        ctx.restore()

        
