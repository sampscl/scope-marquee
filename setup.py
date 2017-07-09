#!/usr/bin/python
from distutils.core import setup

_version = "0.1.0"

setup(name='scope-marquee',
      version=_version,
      description="Python service and zeromq interface to control an SSD1306-based display on a Raspberry Pi 2/3",
      author='Clay Sampson',
      author_email='pdgeek@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      license="MIT",
      requires=["PIL", "zmq", "Adafruit_GPIO", "Adafruit_SSD1306"],
      scripts=['scope-marquee/scope-marquee.py', 'scope-marquee/tell-marquee.py'],
     )
