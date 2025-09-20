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

class Clock():

    beatInterval = 1.0 #seconds
    
    fractionOfBeat = 0

    def __init__(self, app):
        super().__init__()
        self.app = app
        

    def update(self, delta):

        print(repr(self.app.button_states))
        if self.app.button_states.get(BUTTON_TYPES["UP"]):
            self.beatInterval = self.beatInterval * 0.9
        
        if self.app.button_states.get(BUTTON_TYPES["DOWN"]):
            self.beatInterval = self.beatInterval / 0.9

        #self.updateLEDs()

    def background_update(self, delta):


        self.fractionOfBeat = self.fractionOfBeat + (0.001*delta)/self.beatInterval
  
        old = self.fractionOfBeat

        self.fractionOfBeat = self.fractionOfBeat % 1.0

        if old > self.fractionOfBeat:
            pass  #emit a pulse

    

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


    
    def draw(self, ctx):
        
        print("draw clock")

        ctx.save()

        if self.fractionOfBeat < 0.25:
            # draw a circle
            ctx.rgb(120, 234, 0).arc(0,0, 60, 0, 2 * math.pi, True).fill()
      
        ctx.rgb(1,0,0).move_to(-80,0).text(repr(self.beatInterval))
        
        

        ctx.restore()

        
