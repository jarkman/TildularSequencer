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
from frontboards.twentysix import TwentyTwentySix, TOUCH 

class Quantiser():


    def __init__(self, app, sequencerHexpansion, channel, buttonStates):
        super().__init__()
        self.app = app
        self.sequencerHexpansion = sequencerHexpansion
        self.channel = channel
        self.buttonStates = buttonStates
        self.noteEnable = [True]*12 # the notes we are preapred to accept
        self.doQuantise = False
        

    def quantise(self, volts):
        
        #print("quantiser in %f"%(volts))

        if not self.doQuantise:
            return volts
        
        note = volts % 1.0
        octave = volts - note

        minDiff = 2.0
        bestV = -1

        for i in range(12):
            if self.noteEnable[i]:
                diff = abs(i/12.0 - note)
                if diff < minDiff:
                    minDiff = diff
                    bestV = i/12.0

        if bestV > -1:
            #print("quantiser out %f"%(octave+bestV))
        
            return octave+bestV
        
        #print("quantiser - no note!")
        return volts

        
    def buttonDownHandler(self, event):

        
        for i in range(12):
            touchN = i+1 # count 1-12
            
            key = "TOUCH%02d" % (touchN)

            #print("key " + repr(key))

            if TOUCH[key] in event.button:
                self.noteEnable[i] = not self.noteEnable[i]

        if JOYSTICK_BUTTON_TYPES["LEFT"] in event.button:
            self.doQuantise = False
        if JOYSTICK_BUTTON_TYPES["RIGHT"] in event.button:
            self.doQuantise = True   

    def update(self, delta):
        
        for i in range(0, 12):
            if self.noteEnable[i]:
                tildagonos.leds[i+1] = (0, 255, 0)
            else:
                tildagonos.leds[i+1] = (255,0,0)

        tildagonos.leds.write()

        return True
    
        
    def background_update(self, delta):

        # quantiser has nothing to do in the background
        return
    
        
       

    

    
    def draw(self, ctx):
        

        ctx.save()



        ctx.text_align = ctx.CENTER
        ctx.rgb(1,0,0)

        noteNames = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        for note in range(12):
            theta = 2.0*math.pi*note/12.0
            theta = theta - math.pi/2.0 # put 0 at the top
            theta = theta  + (2.0*math.pi)/24.0 # align with the touchpads
        
            x = 90*math.cos(theta)
            y = 90*math.sin(theta)

            ctx.move_to(x,y).text(noteNames[note])

        ctx.move_to(0,0).text("Quantiser")
        ctx.move_to(0,20).text("Ch " + repr(self.channel))
        
        
        if self.doQuantise:
            ctx.rgb(1,0,0).move_to(0,80).text("< Quantised")
        else:    
            ctx.rgb(1,0,0).move_to(0, 80).text("Free >")
        
        ctx.restore()

        
