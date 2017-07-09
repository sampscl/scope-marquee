#!/usr/bin/python

import os

import base64

import sched
import time

import zmq

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from netifaces import interfaces, ifaddresses, AF_INET

class ScopeDisplay(object):

    def __init__(self, disp):
        self.disp = disp
        self.image = Image.new('1', (disp.width, disp.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

        self.context = zmq.Context()
        self.zmq_sock = self.context.socket(zmq.REP)
        self.zmq_sock.bind("tcp://*:5556")
        self.poller = zmq.Poller()
        self.poller.register(self.zmq_sock, zmq.POLLIN)

        self.system_info_enabled = True
    # end __init__

    def initialize_schedule(self, scheduler, now):
        """
        Call once to initialize the schedule and start periodic updates.
        """
        self.__periodic_update(scheduler, now)

    def __periodic_update(self, scheduler, now):
        next_time = now + self.update_period_secs()
        scheduler.enterabs(time = next_time, priority = 1, action = lambda: self.__periodic_update(scheduler, next_time), argument = ())
        self.periodic_update()
    # end periodic_update

    def wait_for_messages(self, time_amount):
        events = dict(self.poller.poll(time_amount * 1000)) # convert to ms for poll
        if events and (events.get(self.zmq_sock) == zmq.POLLIN):
            msg = self.zmq_sock.recv_json(zmq.NOBLOCK)
            while(msg):
                self.zmq_sock.send_json(self.handle_message(msg))
                try: msg = self.zmq_sock.recv_json(zmq.NOBLOCK)
                except: msg = None
            self.update_display()
    # end do_wait_for_messages

    def handle_message(self, msg):
        """
        Handles a message of the form:
            {"action": "action_name", "param": param, ...]}

        This is the prototype for all action_* handlers: return True on success,
        and (False, "reason") on failure. The parameters to action handlers
        will have been serialized and deserialized with JSON so do not do
        anything that JSON data can't do.

        Returns True if message was valid and processed, (False, "reason")
        otherwise.
        """
        if type(msg) != dict or not msg.has_key("action") or not msg.has_key("param"): return (False, "Invalid messsage")

        method = getattr(self, "action_{0}".format(msg["action"]), None)
        if not method: return (False, "Unknown action")

        return method(msg["param"])
    # end handle_message

    def get_system_info_str(self):
        if "/home/pi/hostap/client" == os.path.realpath("/home/pi/hostap/last_run"):
            mode = "cl"
        else:
            mode = "ap"
        return "{0}: {1}".format(mode, ", ".join(ip4_addresses()))
    # end get_system_info_str

    def update_period_secs(self):
        """
        Get the desired time between calls to periodic_update in seconds.
        Fractional seconds are acceptable.
        """
        return 1
    # end update_period_secs
    def periodic_update(self):
        """
        Called once every update_period_secs(). Typically you would draw into
        self.image and then call update_display().
        """
        if not self.system_info_enabled: return
        self.draw_text(self.get_system_info_str(), x=0, y=0)
        self.update_display()
    # end periodic_update

    def update_display(self):
        """
        Send self.image to the display chip and display it.
        """
        self.disp.image(self.image)
        self.disp.display()
    # end update_display

    def draw_text(self, text="", x=0, y=0, clear_first=True):
        w, h = self.text_dim(text)
        if clear_first: self.draw.rectangle((0,y,self.disp.width,y+h), outline=0, fill=0)
        self.draw.text((x,y), text, font=self.font, fill=255)
        return (w,h)
    # end draw_text

    def text_dim(self, text):
        return self.draw.textsize(text, font=self.font)
    # end text_dim

    #
    # Actions handlers
    #

    def action_display_off(self, _params):
        self.disp.command(0xAE)
        return True
    # action_display_off
    def action_display_on(self, _params):
        self.disp.command(0xAF)
        return True
    # end action_display_on
    def action_system_info_off(self, _params):
        self.system_info_enabled = False
        return True
    # end action_system_info_off
    def action_system_info_on(self, _params):
        self.system_info_enabled = True
        return True
    # end action_system_info_on
    def action_set_line(self, params):
        try:
            row = int(params["row"])
            if(row < 1 or row > 6): raise IndexError()
            text = str(params["value"])
            _, h = self.text_dim(text)
            self.draw_text(text, x=0, y=(row-1)*h)
            self.update_display()
            return True
        except:
            return (False, """set_line error, expected "row": 1..6, "value": "string", got {0}""".format(str(params)))
    # end action_set_line
    def action_show_image(self, params):
        try:
            pixels = base64.b64decode(params['pixels'])
            size = params['size']
            mode = params['mode']
            self.image = Image.frombytes(mode, size, pixels).resize((self.disp.width, self.disp.height), Image.BILINEAR).convert('1')
            self.draw = ImageDraw.Draw(self.image)
            self.update_display()
            return True
        except:
            return (False, """show_image error, expected PIL-compatible {'size': [w,h], 'mode': 'RGB (or similar)', 'pixels': '...'}""")
    # end action_show_image
# end class ScopeDisplayBase

def ip4_addresses():
    """
    Get all valid ip addresses on this machine. Does not include the local/lo
    interface.

    Returns: ["192.168.1.1", ...]
    """
    #
    # Thanks Stack Overflow!
    # https://stackoverflow.com/questions/270745/how-do-i-determine-all-of-my-ip-addresses-when-i-have-multiple-nics
    #
    ip_list = []
    for interface in interfaces():
        if interface == u"lo": continue
        if not ifaddresses(interface).has_key(AF_INET): continue
        for link in ifaddresses(interface)[AF_INET]:
            ip_list.append(link[u'addr'])
    return ip_list

def open_display():
    #
    # Thanks Adafruit Industries!
    #

    # Raspberry Pi pin configuration:
    RST = 24
    # Note the following are only used with SPI:
    DC = 23
    SPI_PORT = 0
    SPI_DEVICE = 0
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST,
        dc=DC,
        spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
    return disp
# end open_display

def main():
    disp = open_display()
    disp.begin()
    scope_display = ScopeDisplay(disp)

    s = sched.scheduler(time.time, lambda time_amount: scope_display.wait_for_messages(time_amount))
    scope_display.initialize_schedule(s, time.time())

    s.run()
# end main

if __name__ == '__main__':
    main()
