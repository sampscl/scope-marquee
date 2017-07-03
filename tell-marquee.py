#!/usr/bin/env python

import zmq
import sys
import time

def main():
    context = zmq.Context()
    zmq_sock = context.socket(zmq.REQ)
    zmq_sock.connect("tcp://127.0.0.1:5556")
    # zmq_sock.send_json({"key": sys.argv[1], "value": sys.argv[2]})
    # print("Result: {0}".format(result))
    count=1
    while True:
        zmq_sock.send_json({"key": 1, "value": str(count)})
        result = zmq_sock.recv_json()
        count = count + 1

# end main

if __name__ == '__main__':
    main()
