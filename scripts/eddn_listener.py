import zmq
import zlib

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://eddn.edcd.io:9500")

sub.setsockopt_string(zmq.SUBSCRIBE, "")

print("Listening for messages...")
while True:
    msg = sub.recv_multipart()
    print(zlib.decompress(msg[0]))