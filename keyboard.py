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

class Keyboard():

    beatInterval = 0.5 #seconds
    beat = 0
    numBeats = 4
    maxBeats = 6
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
        self.selectedNote = 0
        self.octave = 0
        if self.channel == 1:
            self.DACSlot = DACSlots.CV1
            self.GateSlot = DACSlots.Gate1
        else:
            self.DACSlot = DACSlots.CV2
            self.GateSlot = DACSlots.Gate2
        
        
    def buttonDownHandler(self, event):

        play = False

        #print("keyboard button event " + repr(event))

       
        # touch pads for notes

        if TOUCH["TOUCH01"] in event.button:
            print("Got TOUCH01")

        newNote = -1

        for i in range(12):
            touchN = i+1 # count 1-12
            
            key = "TOUCH%02d" % (touchN)

            #print("key " + repr(key))

            if TOUCH[key] in event.button:
                newNote = i

        if newNote != -1 and newNote != self.selectedNote:
            play = True

        # joystick for octave
        oldOctave = self.octave

        if JOYSTICK_BUTTON_TYPES["LEFT"] in event.button:
            self.octave = max(self.octave-1, 0)
            play = True
        if JOYSTICK_BUTTON_TYPES["RIGHT"] in event.button:
            self.octave = min(self.octave+1, 3)
            play = True

        if play:

            print("started keyboard note %d"%(newNote))
            self.selectedNote = newNote
            volts = self.octave + self.selectedNote/12.0
            volts = self.quantiser.quantise(volts)

            self.sequencerHexpansion.writeCV(self.DACSlot, volts)
            self.envelope.startEnvelope()
            #self.sequencerHexpansion.startPulse(self.GateSlot)
            

    def update(self, delta):
        
        for i in range(0, 12):
            tildagonos.leds[i+1] = (0, 0, 255)

        tildagonos.leds[self.selectedNote+1] = (0,255,0) 
        tildagonos.leds.write()


        return True
    
        
    def background_update(self, delta):

        # keyboard has nothing to do in the background
        return
    
        
       

    

    
    def draw(self, ctx):
        

        
        
        ctx.save()
        
        big = [False]*12
        big[self.selectedNote] = True
        
        self.app.drawNotes(ctx, None, big)


        ctx.text_align = ctx.CENTER
        ctx.font_size = self.app.fontSize

        ctx.gray(1)

        ctx.move_to(0,0).text("Keyboard")
        ctx.move_to(0,20).text("Ch " + repr(self.channel))
        
        ctx.move_to(0,60).text("Octave")
        ctx.move_to(0,80).text("<- %d +>"%(self.octave))

        ctx.restore()

        
