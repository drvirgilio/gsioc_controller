# gsioc defines a class used for controlling gsioc devices
# ID is an integer
# immediate commands are an ascii string
# buffered commands are an ascii string

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
        s.baudrate = 9600
        s.bytesize = 8
        s.parity = serial.PARITY_NONE
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
        s.flushInput()
        s.write(bytes.fromhex('ff'))
        time.sleep(self.timeout)   # Passively wait for all devices to disconnect
        s.write(ID.to_bytes(1,byteorder='big'))
        resp = s.read(1)    # Will return empty array after timeout
        if(len(resp) == 0):
            raise Exception(str(datetime.datetime.now()) + "No response from device")
        print(str(datetime.datetime.now()) + " -- Connected to device ", ID-128)

    # returns byte array
    # Use str(resp,'ascii') or resp.decode('ascii') to get ascii string
    def iCommand(self,commandstring):
        command = binascii.a2b_qp(commandstring)
        if(command[0] not in range(0,255)):     # Change this to correct range
            raise Exception("Command out of range")
        s = self.serial
        s.flushInput()
        s.write(command[0:1])
        resp = bytearray(0)
        while(True):
            resp_raw = s.read(1)    # Will return empty array after timeout
            if(len(resp_raw) == 0):
                raise Exception(str(datetime.datetime.now()) + "No response from device")
            resp.append(resp_raw[0])
            if(resp[len(resp)-1] > 127):
                resp[len(resp)-1] -= 128
                print(str(datetime.datetime.now()) + " -- Immediate response complete")
                break
            else:
                s.write(bytes.fromhex("06"))
        return resp.decode("ascii")

    def bCommand(self,commandstring):
        data = binascii.a2b_qp("\n" + commandstring + "\r")
        s = self.serial
        s.flushInput()
        resp = bytearray(0)

        # begin buffered command by sending \n until the device echos \n or times out
        firstErrorPrinted = False # This is used to prevent repetitive printing 
        # begin loop
        while(True):
            s.write(data[0:1])    # send line feed
            resp_raw = s.read(1)    # Will return empty array after timeout
            if(len(resp_raw) == 0):
                raise Exception(str(datetime.datetime.now()) + "No response from device")
            readySig = resp_raw[0]
            if(readySig == 10):
                print(str(datetime.datetime.now()) + " -- Starting Buffered command")
                break
            elif(readySig == 35):
                if(not firstErrorPrinted):
                    print("Device busy. Waiting...")
                    firstErrorPrinted = True
            else:
                raise Exception("Did not recieve \\n (0x0A) or # as response")
        resp.append(readySig)

        # Send buffered data
        for i in range(1,len(data)):
            s.write(data[i:i+1])
            resp_raw = s.read(1)    # Will return empty array after timeout
            if(len(resp_raw) == 0):
                raise Exception(str(datetime.datetime.now()) + "No response from device")
            resp.append(resp_raw[0])
            if( resp[i] != data[i] ):
                raise Exception("Recieved " + str(resp,'ascii') + " instead of " + str(data[i:i+1]))
            if( resp[i] == 13 ):
                print(str(datetime.datetime.now()) + " -- Buffered command complete")
                return resp

        # This will happen if sending the data failed
        print(str(datetime.datetime.now()) + " -- Buffered command FAILED")
        resp_no_whitespace = resp[1:len(resp)-2]
        return resp_no_whitespace.decode("ascii")

