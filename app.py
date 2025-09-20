import asyncio
import app
import time
import asyncio
import math

from events.input import Buttons, BUTTON_TYPES
 
from app_components import Menu, Notification, clear_background

from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
from .sequencer import Sequencer
from .clock import Clock
from .turing import Turing

main_menu_items = ["Clock", "Sequencer", "Turing"]


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

        self.clock = Clock(self)
        self.sequencer = Sequencer(self)
        self.turing = Turing(self)

        self.activeMode = self.sequencer
        self.uiMode = self.sequencer
        self.menuActive = True

        self.lastBackgroundUpdate = time.time() * 1000

        self.menu = Menu(
            self,
            main_menu_items,
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )

       

    def select_handler(self, item, idx):

        print("Selecting menu item " + repr(idx))
        if idx == 0:
            self.uiMode = self.clock
            #print("selected clock")
        elif idx == 1:
            self.uiMode = self.sequencer
        elif idx == 2:
            self.uiMode = self.turing

        if self.uiMode != self.clock:  # clock is always active
            self.activeMode = self.uiMode
            
        self.button_states.clear()
        self.menuActive = False

    def back_handler(self):
        #print("back handler")

        if self.menuActive:
            self.minimise()

        self.menuActive = False

    # apparently not called when app is minimised?
    def background_update(self):

        print("background update")

        now = time.time() * 1000.0

        delta = now - self.lastBackgroundUpdate 

        self.lastBackgroundUpdate = now
        
        self.clock.background_update(delta)

        self.activeMode.background_update(delta)

    def update(self, delta):

        if self.menuActive:
            #print("update menu")
            self.menu.update(delta)
            
        else:
            if self.button_states.get(BUTTON_TYPES["CANCEL"]):
                self.button_states.clear()
                if self.menuActive:
                    #print("cancel minimising")
                    self.minimise() 
                else:
                    #print("cancel showing menu")
                    self.menuActive = True


            self.clock.update(delta)
            self.activeMode.update(delta)

        self.background_update()
        
        return True
    


    def draw(self, ctx):

        clear_background(ctx)

        

        if self.menuActive:
            #print("draw menu")
            self.menu.draw(ctx)
        else:
            #print("draw uiMode")
            self.uiMode.draw(ctx)
        
            
        

        

def fmap(self, f, fMin, fMax, oMin, oMax):
    return( oMin + (oMax-oMin)*(f-fMin)/(fMax-fMin))


__app_export__ = TildularSequencer