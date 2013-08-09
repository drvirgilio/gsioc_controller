# gsioc defines a class used for controlling gsioc devices
# ID is an integer
# immediate commands are encoded as a hex string
#   e.g. commandhex = '0b' corresponds to 11 in base 10
# buffered commands are an ascii string
# The commands

import datetime, time
import serial
import binascii

class gsioc:
    def __init__(self,serial=None):
        self.serial = serial

    def createSerial(self,port=0,timeout=0.1):
        self.port = port
        self.timeout = timeout
        # Initiate serial connection
        s = serial.Serial(port)
        #s = serial.serial_for_url("loop://")  # loop for testing
        s.baudrate = 19200
        s.bytesize = 8
        s.parity = serial.PARITY_EVEN
        s.stopbits = 1
        s.timeout = timeout
        self.serial = s
        try :
            s.open()
            print(s)
        except :
            print(s)

    def closeSerial(self):
        self.serial.close()
    
    def connect(self,ID=0):
        if( int(ID) not in range(64) ):
            raise Exception("ID out of range [0,63]")
        ID += 128
        s = self.serial
        s.write(bytes.fromhex('ff'))   
        time.sleep(self.timeout)   # Passively wait for all devices to disconnect
        s.write(ID.to_bytes(1,byteorder='big'))
        resp = s.read(1)    # Will raise serialTimoutException after timeout
        print(str(datetime.datetime.now()) + " -- Connected to device ", ID)

    # returns byte array
    # Use str(resp,'ascii') or resp.decode('ascii') to get ascii string
    def iCommand(self,commandhex):
        command = bytes.fromhex(commandhex)
        if(command[0] not in range(0,255)):     # Change this to correct range
            raise Exception("Command out of range")
        s = self.serial
        s.write(command[0:1])
        resp = bytearray(0)
        while(True):
            resp.append(s.read(1)[0])
            if(resp[len(resp)-1] > 127):
                resp[len(resp)-1] -= 128
                print(str(datetime.datetime.now()) + " -- Immediate response complete")
                break
        return resp

    
    def bCommand(self,commandstring):
        data = binascii.a2b_qp("\n" + commandstring + "\r")
        s = self.serial
        s.write(data[0:1])    # send line feed
        resp = bytearray(0)
        resp.append(s.read(1)[0])
        if(resp[0] != 13):
            print(resp)
            raise Exception("Did not recieve \\r (0x0D) as response")
        for i in range(1,len(data)):
            s.write(data[i:i+1])
            resp.append(s.read(1)[0])
            if( resp[i] != data[i] ):
                raise Exception("Recieved " + str(resp,'ascii') + " instead of " + str(data[i:i+1]))
            if( resp[i] == 13 ):
                print(str(datetime.datetime.now()) + " -- Buffered command complete")
                return resp
        print(str(datetime.datetime.now()) + " -- Buffered command FAILED")
        return resp

