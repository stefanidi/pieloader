#!/usr/bin/env python
 
# (C) 2015 Roman Stefanidi
# redirect data from a TCP/IP connection to a serial port and vice versa
# requires Python 2.2 'cause socket.sendall is used sdfdfdgffdg
 
 
import sys
import os
import time
import threading
import socket
import codecs
import serial
import binascii
 
 
class Redirector:
    def __init__(self, serial_instance, socket_instance):
        self.alive = True
        self.thread_read = threading.Thread()
        self.serial = serial_instance
        self.socket = socket_instance
        self._write_lock = threading.Lock()
 
    def start(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.thread_read = threading.Thread(target=self.writer)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('socket->serial')
        self.thread_read.start()
        self.reader()
 
    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()
 
    def reader(self):
        """loop forever and copy serial->socket"""
        imei = Redirector.tohex(Redirector.getserial())
        while self.alive:
            try:
                data = self.serial.readline()
                # data = data[0:len(data)]
                print('Serial Received {0} bytes: {1}'.format(len(data), data, end=''))
                if data and len(data) == 98:
                    self._write_lock.acquire()
                    try:
                        # remove trailing \r\n
                        # Only consider bytes if started with 4E44
                        # if data[0] == 0x4E and data[1] == 0x44
                        data = data[:-2]
                        # print('Truncated: {0} bytes: {1}'.format(len(data), data, end=''))
                        hex_string = data.decode("utf-8")
                        print('String Data: {0}'.format(hex_string))
                        hex_string = hex_string.replace("4E44383639323639303030303030303030", "4E4438363932363930" + imei)
                        print('Ready Data: {0}'.format(hex_string))
                        byteArrayH = binascii.unhexlify(hex_string)
                        # print('byteArray: {0} bytes: {1}'.format(len(byteArrayH), byteArrayH, end=''))
 
                        # print('A: {0}, B: {1}, Y: {2}, Z: {3}'.format(data[0], data[1], data[len(data)-2], data[len(data)-1]))
                        written = self.socket.send(byteArrayH)  # send it over TCP
                        print('Wrote to socket {0} bytes'.format(written))
                    finally:
                        self._write_lock.release()
            except serial.SerialTimeoutException:
                print('Reader cont')
                continue
            except socket.error as ex:
                print('READER ERROR: %s' % ex)
                # probably got disconnected
                break
            except:
                print("Unexpected error: %s" % sys.exc_info()[0])
                continue
        print('Reader exiting. Alive: {0}'.format(self.alive))
        self.alive = False
 
    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                print('Socket Received: {0}'.format(data.decode('UTF-8')))
                if not data:
                    break
                written = self.serial.write(data)  # get a bunch of bytes and send them
                print('Wrote to socket {0} bytes'.format(written))
            except socket.timeout:
                print('Writer cont')
                continue
            except socket.error as ex:
                print('WRITER ERROR: %s' % ex)
                # probably got disconnected
                break
        print('Writer exiting. Alive: {0}'.format(self.alive))
        self.alive = False
        self.thread_read.join()
 
    @staticmethod
    def getserial():
	return "16450455"
        # Extract serial from cpuinfo file
        cpuserial = "00000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[18:26]
            f.close()
        except:
            cpuserial = "4a12b52c"  # "00000000"
        return cpuserial
 
    @staticmethod
    def tohex(inp):
        return "".join("{:02x}".format(ord(c)) for c in inp)
 
 
if __name__ == '__main__':
    import optparse
 
    parser = optparse.OptionParser(usage="%prog [port]",
                                   description="Shinbone Serial Interface."
                                   )
 
    parser.add_option("-p", "--port",
                      dest="port",
                      help="port number (default 4600)",
                      default=4600
                      )
 
    (options, args) = parser.parse_args()
 
    # get port for the TCP service
    port = options.port
    host = 'manage.shinbone.com.au'
 
    while True:
        try:
            # connect to serial port
            ser = serial.Serial('/dev/ttyAMA0', timeout=120)
 
            # connect to tcp service
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(120.0)
            client.connect((host, port))
            print('\nConnected to {0}:{1}'.format(host, port))
 
            # enter network <-> serial loop
            r = Redirector(
                ser,
                client,
            )
            r.start()
 
            client.close()
            ser.close()
        except KeyboardInterrupt:
            break
        except socket.error as ex:
            print('MAIN ERROR: %s' % ex)
            ser.close()
 
    ser.close()
    print('\n--- exit ---\n')  # sys.stderr.write('\n--- exit ---\n')
