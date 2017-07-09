#!/usr/bin/env python

import zmq
import sys
import time
from PIL import Image
import base64

def main():
    context = zmq.Context()
    zmq_sock = context.socket(zmq.REQ)
    zmq_sock.connect("tcp://sampson-scope:5556")
    cmd = sys.argv[1]
    target = sys.argv[2]
    param = {}
    if target == "show_image":
        image = Image.open(sys.argv[3])
        param = {
            'pixels': base64.b64encode(image.tobytes()),
            'size': image.size,
            'mode': image.mode,
            }
    elif len(sys.argv) > 3:
        param = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    msg = {cmd: target, "param": param} # e.g. {'action': 'set_line', 'param': {'row': 1, 'value': 'your text here'}}
    zmq_sock.send_json(msg)
    result = zmq_sock.recv_json()
    print("Result: {0}".format(result))
# end main

if __name__ == '__main__':
    main()
