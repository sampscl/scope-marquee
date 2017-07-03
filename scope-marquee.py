#!/usr/bin/env python

import sched
import time

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
    # end __init__

    @staticmethod
    def update_display(instance, scheduler, now):
        instance.do_update_display(scheduler, now)
    # end update_display

    def do_update_display(self, scheduler, now):
        next_time = now + 1
        scheduler.enterabs(time = next_time, priority = 1, action = ScopeDisplay.update_display, argument = (self, scheduler, next_time))

        # clear
        self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)

        h = 0
        lines = [
            "Hello, World!",
            "{:.0f}".format(now),
        ]
        for l in lines: h += self.line_draw(l, h)

        # load image into the chip
        self.disp.image(self.image)

        # show image on screen
        self.disp.display()
    # end do_update_display

    def line_draw(self, line, accum):
        _w, h = self.draw.textsize(line, font=self.font)
        self.draw.text((0,accum), line, font=self.font, fill=255)
        return accum + h
    # end line_draw

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
    s = sched.scheduler(time.time, time.sleep)
    ScopeDisplay.update_display(ScopeDisplay(disp), s, time.time())
    s.run()
# end main

if __name__ == '__main__':
    main()
