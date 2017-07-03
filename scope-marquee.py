#!/usr/bin/env python

import sched
import time

import zmq

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class ScopeDisplay(object):
    def __init__(self, disp):
        self.disp = disp
        self.image = Image.new('1', (disp.width, disp.height))
        self.font = ImageFont.load_default()
        self.draw = ImageDraw.Draw(self.image)
        # 128x64 display can show 21x6 characters with the default font; the last line will be clipped a few pixels
        #                "012345678901234567890",
        #                "012345678901234567890",
        #                "012345678901234567890",
        #                "012345678901234567890",
        #                "012345678901234567890",
        #                "012345678901234567890",
        self.lines = {1: "There".center(21, " "),
                      2: "Are".center(21, " "),
                      3: "No".center(21, " "),
                      4: "Messages".center(21, " "),
                      5: "To".center(21, " "),
                      6: "Display".center(21, " "),
        }

        self.context = zmq.Context()
        self.zmq_sock = self.context.socket(zmq.REP)
        self.zmq_sock.bind("tcp://*:5556")
        self.poller = zmq.Poller()
        self.poller.register(self.zmq_sock, zmq.POLLIN)
    # end __init__

    def update_display(self, scheduler, now):
        next_time = now + 1
        scheduler.enterabs(time = next_time, priority = 1, action = lambda: self.update_display(scheduler, next_time), argument = ())

        # clear
        self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)

        y = 0
        for _, line in sorted(self.lines.iteritems()): y += self.line_draw(line, y)

        # load image into the chip
        self.disp.image(self.image)

        # show image on screen
        self.disp.display()
    # end do_update_display

    def line_draw(self, line, y):
        self.draw.text((0,y), line, font=self.font, fill=255)
        _w, y = self.draw.textsize(line, font=self.font)
        return y
    # end line_draw

    def wait_for_messages(self, time_amount):
        events = dict(self.poller.poll(time_amount * 1000)) # convert to ms for poll
        if events and (events.get(self.zmq_sock) == zmq.POLLIN):
            self.handle_message(self.zmq_sock.recv_json(zmq.NOBLOCK))
    # end do_wait_for_messages

    def handle_message(self, msg):
        if type(msg) != dict or not msg.has_key("key") or not msg.has_key("value"):
            self.zmq_sock.send_json((False, "Invalid message"))
        else:
            self.lines[int(msg["key"])] = msg["value"]
            self.zmq_sock.send_json(True)
# end ScopeDisplay

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
    ScopeDisplay.update_display(scope_display, s, time.time())

    s.run()
# end main

if __name__ == '__main__':
    main()
