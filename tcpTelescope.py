#!/usr/bin/env python
# -*- coding: utf-8 -*-

#An adaption of a TCPTelescope, piping to arduino

#Thank you to Sven Steinbauer (https://github.com/Svenito) for the basis of this code

#Arduino communications added by Keegan Crankshaw (http://github.com/kcranky)

import struct, time, socket, select, serial, ephem
from math import *

M_PI =  3.1415926535897932385

# List of socket objects that are currently open
open_sockets = []

#add the objects for ephem
ct = ephem.city('Cape Town')
ct.long="33:57:28.42"
ct.lat="-18:27:40.51"
#ct.elevation = 106

#Get the arduino serial port
#Use an int 1 value below the actual com port
arduino = serial.Serial(7, 9600)

# AF_INET means IPv4.
# SOCK_STREAM means a TCP connection.
# SOCK_DGRAM would mean an UDP "connection".
listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# The parameter is (host, port).
# The host, when empty or when 0.0.0.0, means to accept connections for
# all IP addresses of current machine. Otherwise, the socket will bind
# itself only to one IP.
# The port must greater than 1023 if you plan running this script as a
# normal user. Ports below 1024 require root privileges.
listening_socket.bind( ("", 10001) )

# The parameter defines how many new connections can wait in queue.
# Note that this is NOT the number of open connections (which has no limit).
# Read listen(2) man page for more information.
listening_socket.listen(5)

current_position = []

def printit(ra_int, dec_int):
    h = ra_int
    d = floor(0.5 + dec_int*(360*3600*1000/4294967296.0));
    dec_sign = ''
    if d >= 0:
        if d > 90*3600*1000:
            d =  180*3600*1000 - d;
            h += 0x80000000;
        dec_sign = '+';
    else:
        if d < -90*3600*1000:
            d = -180*3600*1000 - d;
            h += 0x80000000;
        d = -d;
        dec_sign = '-';
    
    
    h = floor(0.5+h*(24*3600*10000/4294967296.0));
    ra_ms = h % 10000; h /= 10000;
    ra_s = h % 60; h /= 60;
    ra_m = h % 60; h /= 60;
    
    h %= 24;
    dec_ms = d % 1000; d /= 1000;
    dec_s = d % 60; d /= 60;
    dec_m = d % 60; d /= 60;
    
    ephemra = str(trunc(h)) +':'+ str(trunc(ra_m)) +':'+ str(trunc(ra_s)) +'.'+ str(trunc(ra_ms))
    ephemdec = str(dec_sign) + str(trunc(d)) +':'+ str(trunc(dec_m)) +':'+ str(trunc(dec_s)) +'.'+ str(trunc(dec_ms))
    
    
    #print("ra =", h,"h", ra_m,"m",ra_s,".",ra_ms, sep=" ")
    #print("dec =",dec_sign, d,"d", dec_m,"m",dec_s,".",dec_ms)
    #print("ephemra =" + ephemra)
    #print("ephemdec =" +ephemdec)
    
    star = ephem.Equatorial(ephemra, ephemdec)
    body = ephem.FixedBody()
    body._ra = star.ra
    body._dec = star.dec
    body._epoch = star.epoch    
    body.compute(ct)
    #print("azimuth= " + str(body.az))
    #print("altitude= " + str(body.alt))
    altToArd(body.alt)
    azToArd(body.az)
    
#NB: The methods makes 2 assumptions
#1) The motor steps 0.9 degrees,
#2) The gear ratio on the azimuth is 2:1
#I have commented where these values come into play. adjust them as need be

def altToArd(alt):
    nalt = str(alt)
    nalt = nalt[:nalt.index(':')]
    arduino.write(b'y')
    nalt = int(nalt)/360*400 #Conversion of 360 degrees to 400 degrees
    time.sleep(0.01)
    for i in range(0, int(nalt)):
        arduino.write(b's')
        time.sleep(0.01)
    arduino.write(b'e')

def azToArd(az):
    naz = str(az)
    naz = naz[:naz.index(':')]
    arduino.write(b'x')
    time.sleep(0.01)
    naz = int(naz)/360*400 #Conversion of 360 degrees to 400 degrees
    for i in range(0, int(naz)*2): #Gearing ratio is 2
        arduino.write(b's')
        time.sleep(0.01)
    arduino.write(b'e')
    print('data sent')
    

while True:
    # Waits for I/O being available for reading from any socket object.
    rlist, wlist, xlist = select.select( [listening_socket] + open_sockets, [], [] )
    for i in rlist:
        if i is listening_socket:
            new_socket, addr = listening_socket.accept();
            open_sockets.append(new_socket);
        else:
            data = i.recv(1024)
            if data == "":
                open_sockets.remove(i)
                print("Connection closed")
            else:
                #print( repr(data))
                data = struct.unpack("3iIi", data)
                #print(data)
                #print("%x, %o" % (data[3], data[3]))
                ra = data[3]*(M_PI/0x80000000)
                dec = data[4]*(M_PI/0x80000000)
                cdec = cos(dec)

                desired_pos = []
                desired_pos.append(cos(ra)*cdec)
                desired_pos.append(sin(ra)*cdec)
                desired_pos.append(sin(dec))
                printit(data[3], data[4])
                #print(desired_pos)
                
                #Set desired position and get current
                #send current position back to client
                #update current position                
                reply = struct.pack("3iIii", 24, 0, int(time.time()), data[3], data[4], 0)
                #print (repr(reply))
                #print(i.send(reply))
