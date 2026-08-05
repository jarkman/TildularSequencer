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

        self.currentInput = None
        self.currentOutput = None
        

    def quantise(self, volts):
        
        #print("quantiser in %f"%(volts))

        self.currentInput = volts
        self.currentOutput = volts
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
        
            self.currentOutput = octave+bestV
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

        self.app.drawNotes(ctx, self.noteEnable, None)

        # draw a line to show the mapping we're doing
        if self.currentInput is not None and self.currentOutput is not None:

            radiusInput = 40
            inNote = self.currentInput%1.0
            thetaInput = 2.0*math.pi*inNote
            thetaInput = thetaInput - math.pi/2.0 # put 0 at the top
            thetaInput = thetaInput  + (2.0*math.pi)/24.0 # align with the touchpads


            radiusOutput = 100
            outNote = self.currentOutput%1.0
            thetaOutput = 2.0*math.pi*outNote
            thetaOutput = thetaOutput - math.pi/2.0 # put 0 at the top
            thetaOutput = thetaOutput  + (2.0*math.pi)/24.0 # align with the touchpads
            
            radiusMid = 80

            xInput = radiusInput*math.cos(thetaInput)
            yInput = radiusInput*math.sin(thetaInput)
            
            xMid = radiusMid*math.cos(thetaInput)
            yMid = radiusMid*math.sin(thetaInput)

            xOutput = radiusOutput*math.cos(thetaOutput)
            yOutput = radiusOutput*math.sin(thetaOutput)

            ctx.rgb(0.3,0.3,1.0)
            ctx.move_to(xInput,yInput).line_to(xMid,yMid).line_to(xOutput,yOutput)
            ctx.stroke()
       
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.ALPHABETIC
        ctx.font_size = self.app.fontSize
        ctx.gray(1)
        ctx.move_to(0,0).text("Quantiser")
        ctx.move_to(0,ctx.font_size).text("Ch " + repr(self.channel))
        
        
        if self.doQuantise:
            ctx.move_to(0,80).text("< Quantised")
        else:    
            ctx.move_to(0, 80).text("Free >")
        
        ctx.restore()

        
