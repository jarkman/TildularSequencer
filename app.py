import asyncio
import app
import time
import asyncio
import math

from events.input import Buttons, BUTTON_TYPES
 
from app_components import Menu, Notification, clear_background

from .sequencerHexpansion import SequencerHexpansion
from tildagonos import tildagonos
from system.eventbus import eventbus
from events.input import BUTTON_TYPES, ButtonDownEvent
from system.patterndisplay.events import PatternDisable
from .sequencer import Sequencer
from .keyboard import Keyboard
from .tilt import Tilt
from .envelope import Envelope
from .quantiser import Quantiser
from .clock import Clock
from .turing import Turing


# to simulate, 
# cd C:\Tildagon\badge-2024-software\sim
# pipenv run python run.py

# deploy to badge: https://tildagon.badge.emfcamp.org/tildagon-apps/run-on-badge/
# seem to need to do each file individually?

# handy links

# this app
# https://github.com/jarkman/TildularSequencer

# PCB design files
# TODO

# 2026 button names
# https://github.com/emfcamp/badge-2024-software/blob/a412e00df9cd187437dacd702724aad9cb0d0d9d/modules/frontboards/twentysix.py#L109

# test app for the sequencer hexpansion
# https://github.com/thawney/Tildular/blob/main/Tildular_Test/app.py

# Tildagon dec docs
# https://tildagon.badge.emfcamp.org/tildagon-apps/reference/reference/





# TODO - copy update strategy from https://github.com/MatthewWilkes/md-updater/blob/main/sega.py


main_menu_items = ["Clock", "Sequencer 1", "Sequencer 2", "Keyboard 1", "Keyboard 2", "Tilt 1", "Tilt 2", "Envelope 1", "Envelope 2", "Quantiser 1", "Quantiser 2", "Turing"]


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

        self.sequencerHexpansion = SequencerHexpansion()

        self.clock = Clock(self)

        self.envelope1 = Envelope(self, self.sequencerHexpansion, 1, self.button_states)
        self.envelope2 = Envelope(self, self.sequencerHexpansion, 2, self.button_states)
        
        self.quantiser1 = Quantiser(self, self.sequencerHexpansion, 1, self.button_states)
        self.quantiser2 = Quantiser(self, self.sequencerHexpansion, 2, self.button_states)

        self.sequencer1 = Sequencer(self, self.sequencerHexpansion, 1, self.button_states,self.envelope1, self.quantiser1)
        self.sequencer2 = Sequencer(self, self.sequencerHexpansion, 2, self.button_states, self.envelope2, self.quantiser2)

        self.keyboard1 = Keyboard(self, self.sequencerHexpansion, 1, self.button_states, self.envelope1, self.quantiser1)
        self.keyboard2 = Keyboard(self, self.sequencerHexpansion, 2, self.button_states, self.envelope2, self.quantiser2)

        self.tilt1 = Tilt(self, self.sequencerHexpansion, 1, self.button_states,self.envelope1, self.quantiser1)
        self.tilt2 = Tilt(self, self.sequencerHexpansion, 2, self.button_states,self.envelope2, self.quantiser2)
        
        self.turing = Turing(self)

        self.activeMode1 = self.sequencer1
        self.activeMode2 = self.sequencer2
        self.uiMode = self.sequencer1
        self.menuActive = True

        self.lastBackgroundUpdate = time.time() * 1000

        self.menu = Menu(
            self,
            main_menu_items,
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )

        eventbus.on_async(ButtonDownEvent, self.buttonDownHandler, self)
       
    async def buttonDownHandler(self, event):

        #print("app button event " + repr(event))

        #layout_handled = await self.layout.button_event(event)
        #if not layout_handled:
        if not self.menuActive:
            #print("app button forwarding to " + repr(self.uiMode))
            self.uiMode.buttonDownHandler(event)
        else:
            print("... ignoring, menu up")

    def select_handler(self, item, idx):

        if not self.menuActive:
            return
        
        print("Selecting menu item " + repr(idx))
        if idx == 0:
            self.uiMode = self.clock
            #print("selected clock")
        elif idx == 1:
            self.uiMode = self.sequencer1
            self.activeMode1 = self.uiMode
        elif idx == 2:
            self.uiMode = self.sequencer2
            self.activeMode2 = self.uiMode
        elif idx == 3:
            self.uiMode = self.keyboard1
            self.activeMode1 = self.uiMode
        elif idx == 4:
            self.uiMode = self.keyboard2
            self.activeMode2 = self.uiMode
        elif idx == 5:
            self.uiMode = self.tilt1
            self.activeMode1 = self.uiMode
        elif idx == 6:
            self.uiMode = self.tilt2
            self.activeMode2 = self.uiMode
        elif idx == 7:
            self.uiMode = self.envelope1  # envelope and quantiser don't make notes on their own so we don't set an active mode for them
        elif idx == 8:
            self.uiMode = self.envelope2
        elif idx == 9:
            self.uiMode = self.quantiser1 
        elif idx == 10:
            self.uiMode = self.quantiser2
        elif idx == 11:
            self.uiMode = self.turing

       
        self.button_states.clear()
        self.menuActive = False

    def back_handler(self):
        #print("back handler")

        if self.menuActive:
            self.minimise()

        self.menuActive = False

    # apparently not called when app is minimised?
    def background_update(self, delta):

        #print("app background update")

        now = time.time() * 1000.0

        #delta = now - self.lastBackgroundUpdate 

        self.lastBackgroundUpdate = now
        
        self.clock.background_update(delta)

        self.sequencerHexpansion.update(delta)

        
        self.activeMode1.background_update(delta)
        self.activeMode2.background_update(delta)

        self.envelope1.background_update(delta)
        self.envelope2.background_update(delta)

    def update(self, delta):

        #print("app update")

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

            
            self.uiMode.update(delta)

       
        
        return True
    


    def draw(self, ctx):

        ctx.save()

        clear_background(ctx)

        

        if self.menuActive:
            #print("draw menu")
            self.menu.draw(ctx)
        else:
            #print("draw uiMode")
            self.uiMode.draw(ctx)
        
        if not self.sequencerHexpansion.gotHexpansion():
            ctx.rgb(1,0,0).move_to(-80,0).text("No hexpansion!")

        ctx.restore()    
        

        

def fmap(self, f, fMin, fMax, oMin, oMax):
    return( oMin + (oMax-oMin)*(f-fMin)/(fMax-fMin))


__app_export__ = TildularSequencer