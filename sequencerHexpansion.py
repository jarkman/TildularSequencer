import app

from app_components import clear_background
from events.input import Buttons, BUTTON_TYPES
from time import sleep_ms, ticks_diff, ticks_ms


ADS1015_ADDR = 0x48
MCP4728_ADDRS = tuple(range(0x60, 0x68))

ADC_LABELS = ("Pot A", "Range", "CLK IN", "RST IN")
DAC_LABELS = ("CV1", "Gate1", "CV2", "Gate2")


ADS_FSR_VOLTS = 4.096
ADS_PGA_4V096 = 0x0200
ADS_DR_1600SPS = 0x0080

ADC_INTERVAL_MS = 100
DAC_INTERVAL_MS = 700
PORT_INTERVAL_MS = 2000


def u16_bytes(value):
    return bytes(((value >> 8) & 0xFF, value & 0xFF))


def dac_code(volts):
    volts = max(0, min(3.3, volts))
    return round(volts * 4095 / 3.3)


def find_inserted_port():
    try:
        from system.hexpansion.app import HexpansionManagerApp
    except ImportError:
        return None

    for index, pin in enumerate(HexpansionManagerApp.hexpansion_pins):
        try:
            if not pin.value():
                return index + 1
        except Exception:
            pass
    return None


def get_i2c_for_port(port):
    try:
        from system.hexpansion.config import HexpansionConfig
    except ImportError:
        return None

    try:
        return HexpansionConfig(port).i2c
    except Exception:
        return None


def find_dac_addr(addresses):
    for addr in MCP4728_ADDRS:
        if addr in addresses:
            return addr
    return None


def write_dac(i2c, address, values):
    packet = bytearray()
    for value in values:
        value = max(0, min(4095, int(value)))
        packet.append((value >> 8) & 0x0F)
        packet.append(value & 0xFF)
    i2c.writeto(address, packet)


def read_adc_raw(i2c, channel):
    mux = (0x04 + channel) << 12
    config = (
        0x8000
        | mux
        | ADS_PGA_4V096
        | 0x0100
        | ADS_DR_1600SPS
        | 0x0003
    )

    i2c.writeto_mem(ADS1015_ADDR, 0x01, u16_bytes(config))
    sleep_ms(2)

    data = i2c.readfrom_mem(ADS1015_ADDR, 0x00, 2)
    raw = (data[0] << 8) | data[1]
    if raw & 0x8000:
        raw -= 0x10000
    return raw >> 4


def read_adc_volts(i2c, channel):
    raw = read_adc_raw(i2c, channel)
    return raw, raw * ADS_FSR_VOLTS / 2048

class ADCSlots:
    Pitch = 0
    Speed = 1
    ClockIn = 2
    ResetIn = 3

class DACSlots:
    CV1 = 0
    Gate1 = 1
    CV2 = 2
    Gate2 = 3


class SequencerHexpansion():
    def __init__(self, config=None):
        
        self.port = None
        self.i2c = None
        self.adc_found = False
        self.dac_addr = None

        self.adc = [(0, 0.0)] * 4
        self.dac = [0] * 4
        self.pulseEndTime = [0] * 4
        self.dac_step = 0

        
        self.last_adc_ms = 0
        self.last_dac_ms = 0
        self.last_port_ms = 0

        if config:
            self.port = config.port
            self.i2c = config.i2c
            self.scan_i2c()
        else:
            self.refresh_port()

    def gotHexpansion(self):
        return self.port != None
    
    def writeCV(self, slot, volts):

        if self.dac_addr is None:
            print("writeCV - no DAC")
            return

        #value is a float 0-3.3
        print("writeCV volts " + repr(volts))
        try:
            code = dac_code(volts)
            print("dacCode " + repr(code))
            self.dac[slot] = code
            print("slot val " + repr(self.dac[slot]))
            write_dac(self.i2c, self.dac_addr, self.dac)
        except Exception as e:
            #self.dac_addr = None
            print("writeCV exception "+ repr(e))

    def startPulse(self, slot):

        if self.dac_addr is None:
            print("startPulse - no DAC")
            return
        
        try:
            code = dac_code(3.3)
            self.dac[slot] = code
            write_dac(self.i2c, self.dac_addr, self.dac)
            self.pulseEndTime[slot] = ticks_ms() + 100

        
        except Exception as e:
            #self.dac_addr = None
            print("startPulse exception "+ repr(e))

    def endPulses(self):
        # see if it's time to stop any pulses

        if self.dac_addr is None:
            print("endPulses - no DAC")
            return

        now = ticks_ms()
        for slot in range(4):
            if self.pulseEndTime[slot] > 0 and self.pulseEndTime[slot] < now:

                try:
                    dac_code = dac_code(0.0)
                    self.dac[slot] = dac_code
                    write_dac(self.i2c, self.dac_addr, self.dac)
                    self.pulseEndTime[slot] = 0

                
                except Exception as e:
                     #self.dac_addr = None
                    print("endPulses exception "+ repr(e))


    def refresh_port(self):
        port = find_inserted_port()
        if port == self.port:
            return

        self.port = port
        self.i2c = get_i2c_for_port(port) if port is not None else None
        self.scan_i2c()

    def scan_i2c(self):
        self.adc_found = False
        self.dac_addr = None

        if self.i2c is None:
            return

        try:
            addresses = self.i2c.scan()
        except Exception:
            return

        self.adc_found = ADS1015_ADDR in addresses
        self.dac_addr = find_dac_addr(addresses)

    def update(self, delta):
        
        now = ticks_ms()

        if ticks_diff(now, self.last_port_ms) >= PORT_INTERVAL_MS:
            self.last_port_ms = now
            self.refresh_port()
            self.scan_i2c()

        if self.i2c is None:
            return

        self.endPulses()

        #if self.dac_addr is not None:
         #   self.update_dac(now)
        if self.adc_found:
            self.update_adc(now)

    def update_dac(self, now):

        # UNUSED

        if ticks_diff(now, self.last_dac_ms) < DAC_INTERVAL_MS:
            return
        self.last_dac_ms = now

        patterns = (
            (0.0, 0.0, 0.0, 0.0),
            (0.8, 0.8, 0.8, 0.8),
            (1.6, 1.6, 1.6, 1.6),
            (2.4, 2.4, 2.4, 2.4),
            (3.3, 3.3, 3.3, 3.3),
            (0.0, 1.1, 2.2, 3.3),
        )

        self.dac = [dac_code(volts) for volts in patterns[self.dac_step]]
        self.dac_step = (self.dac_step + 1) % len(patterns)

        try:
            write_dac(self.i2c, self.dac_addr, self.dac)
        except Exception:
            self.dac_addr = None

    def update_adc(self, now):
        if ticks_diff(now, self.last_adc_ms) < ADC_INTERVAL_MS:
            return
        self.last_adc_ms = now

        try:
            self.adc = [read_adc_volts(self.i2c, channel) for channel in range(4)]
        except Exception:
            self.adc_found = False

