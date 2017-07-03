#!/usr/bin/env python

import zmq
import sys

def main():
    context = zmq.Context()
    zmq_sock = context.socket(zmq.REQ)
    zmq_sock.connect("tcp://127.0.0.1:5556")
    zmq_sock.send_json({"key": sys.argv[1], "value": sys.argv[2]})
    result = zmq_sock.recv_json()
    print("Result: {0}".format(result))
# end main

if __name__ == '__main__':
    main()
