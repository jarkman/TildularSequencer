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


def fmap(f, fMin, fMax, oMin, oMax):
    return( oMin + (oMax-oMin)*(f-fMin)/(fMax-fMin))

class Envelope():

   
    fractionOfBeat = 0

    def __init__(self, app, sequencerHexpansion, channel, buttonStates):
        super().__init__()
        self.app = app
        self.sequencerHexpansion = sequencerHexpansion
        self.channel = channel
        self.buttonStates = buttonStates

        self.envelopeStart = 0.0
        self.playing = False

        # set up a pulse
        self.gain = [0.0]*6
        self.gain[0] = 1.0
        self.gain[1] = 0.5

        self.step = 0
        self.selectedStep = -1

        if self.channel == 1:  
            self.GateSlot = DACSlots.Gate1
        else:
            self.GateSlot = DACSlots.Gate2
           
        
    def buttonDownHandler(self, event):

        return

    def startEnvelope(self):
        now = time.ticks_ms() / 1000.0
        self.playing = True

        self.envelopeStart = now

        #print("started self.envelopeStart %f " % (self.envelopeStart))

        self.step = 0 # assuming clock.fractionOfBeat is also 0 here
        self.background_update(0)
        
    def update(self, delta):
        
        if TwentyTwentySix.touch_states["TOUCH01"][0]:
            self.selectedStep = 0
        elif TwentyTwentySix.touch_states["TOUCH03"][0]:
            self.selectedStep = 1
        elif TwentyTwentySix.touch_states["TOUCH05"][0]:
            self.selectedStep = 2
        elif TwentyTwentySix.touch_states["TOUCH07"][0]:
            self.selectedStep = 3
        elif TwentyTwentySix.touch_states["TOUCH09"][0]:
            self.selectedStep = 4
        elif TwentyTwentySix.touch_states["TOUCH11"][0]:
            self.selectedStep = 5
        else:
            self.selectedStep = -1        

        # only use odd-numbered LEDs
        for i in range(0, 12):
            if i%2 == 0 :
                tildagonos.leds[i+1] = (0, 255, 0) # light up active ones green
            else:
                tildagonos.leds[i+1] = (0, 0, 0)

        if self.selectedStep > -1:
            tildagonos.leds[self.selectedStep*2+1] = (0, 0, 255) # selected one is blue

            # update CV vaue from knob
            gain = self.sequencerHexpansion.adc[ADCSlots.Pitch][1] / 3.3
            #print("new note volts " + repr(volts))
            self.gain[self.selectedStep] = gain
            
            
        tildagonos.leds.write()

        return True
    
        
    def background_update(self, delta):

        # for sequencer, we could take the absolute time from the clock
        # but for keyboard, we want to start from when the keyboard is clicked

        
        if not self.playing:
            #print("channel %d not playing" % (self.channel))
            return
        
        now = time.ticks_ms() / 1000.0

        #print("now %f self.envelopeStart %f " % (now, self.envelopeStart))

        #print("now - self.envelopeStart %f self.app.clock.beatInterval %f" % (now - self.envelopeStart, self.app.clock.beatInterval))

        newStep =  int((now - self.envelopeStart)*6.0/self.app.clock.beatInterval)

        #print("channel %d newStep %d" % (self.channel, newStep))

        if newStep > 5:
            self.playing = False
            return
        
        if newStep > self.step:
            self.step = newStep

            if self.step < 6:
                # clock out the envelope as time goes by
                g = self.gain[self.step]
            

                volts = fmap(g, 0.0, 1.0, 0, MAX_VOLTS)

                self.sequencerHexpansion.writeCV(self.GateSlot, volts)


        return
    
        
       

    

    
    def draw(self, ctx):
        

        ctx.save()


        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()

        for step in range(0,6):
            x1 = fmap(step, 0, 6, -100, 100)
            x2 = fmap(step+1, 0, 6, -100, 100)
            y1 = 5
            y2 = - self.gain[step]* 50
            r = 0.5
            g = 0.5
            b = 0.5
            if self.step == self.selectedStep:
                g = 1.0
            elif self.step == step:
                r = 1.0
            
            ctx.rgb(r, g, b).rectangle(x1, y1, x2-x1, y2-y1).fill()

        #if self.acc_read:
        #    ctx.rgb(1, 0, 0).move_to(-80, -40).text(
        #        "accel x,y,z:\n{},\n{},\n{}".format(
        #            self.acc_read[0], self.acc_read[1], self.acc_read[2]))
        #else:
        #    ctx.rgb(1, 0, 0).move_to(-80, 0).text("no readings yet")


        ctx.text_align = ctx.CENTER
        ctx.rgb(1,0,0)
        ctx.move_to(0,0).text("Envelope")
        ctx.move_to(0,20).text("Ch " + repr(self.channel))
        
        ctx.restore()

        
