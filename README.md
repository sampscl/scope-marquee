# Scope Marquee

Control a SSD1306 OLED display on a Raspberry Pi 2 or 3.

## Installation (from cloned repo)

1. Clone the repo ```git clone https://github.com/sampscl/scope-marquee.git```
2. Install ```cd scope-marquee; sudo python setup.py install```

## Check it out

```tell-marquee action set_line row 1 value "Hello, world."```

You must have enabled your Pi's SPI bus and wired the display correctly. The
raspi-config program can be used to enable SPI, and a great SPI pinout website
is https://pinout.xyz/pinout/spi.
