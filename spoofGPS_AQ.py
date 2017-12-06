"""
uBlox UBX protocol spoofer for AutoQuad

Author: Kristian Husum Terkildsen, khte@mmmi.sdu.dk

Notes to dev: 
* Try other baud rates? 9600?
* Add TIM-TP and AID-REQ?

Sources of inspiration:
* https://github.com/deleted/ublox/blob/master/message.py
"""

import serial
import struct
import time
import datetime

def readAndPrint(port):
	readByte = port.read()
	print hex(ord(readByte))
	return readByte

class UBXSpoofer():
	def __init__(self):
		self.ser0 = serial.Serial(port = "/dev/ttyUSB0") #, baudrate = 230400
		#UBX header and ID's
		self.SYNC = b"\xb5\x62"
		self.NAV_VELNED = b"\x01\x12"
		self.NAV_POSLLH = b"\x01\x02"
		self.NAV_DOP = b"\x01\x04"
		self.NAV_TIMEUTC = b"\x01\x21"
		self.messageClass = ""
		self.messageID = ""
		self.baudFound = False
	
	def startSpoofing(self):
		#Find the requested baud rate
		while not self.baudFound:
			readByte = self.ser0.read()
			if readByte == "\xb5":
				readBytes = self.ser0.read(3)
				if readBytes[1] == "\x06" and readBytes[2] == "\x00":
					print "CFG-PRT"
					readBytes = self.ser0.read(14)
					print type(readBytes)
					baudBytes = readBytes[10:]
					print hex(ord(baudBytes[0])), hex(ord(baudBytes[1])), hex(ord(baudBytes[2])), hex(ord(baudBytes[3]))

		#ser.baudrate = 115200
		
		#Send positional data to flight controller
		while True:
			GPSMsToW = self.calcMsToW()
			
			#read positional data from source (optionally velocity data also)
			#convert to geodetic coordinates if necessary
			
			#self.sendNAV_VELNED(self,GPSMsToW, velN, velE, velD, speed, gSpeed, heading, speedAcc, headingAcc)
			self.sendNAV_POSLLH(GPSMsToW, 21.279168, -157.835318, 10000, 10000, 10, 10)
			self.sendNAV_DOP(GPSMsToW, 1, 1, 1, 1, 1, 1, 1)
			#self.sendNAV_TIMEUTC(GPSMsToW, tAcc, nano, year, month, day, hour, minute, sec, valid)

	def checksum(self, message):
		CK_A = 0x00
		CK_B = 0x00
		buf = buffer(message)
		for i in buf:
			CK_A += ord(i) #Return integer value representing the character
			CK_A &= 255
			CK_B += CK_A
			CK_B &= 255
		return struct.pack('BB', CK_A, CK_B)
	
	def calcMsToW(self):
		weekday = datetime.datetime.today().weekday()
		time = datetime.datetime.now()
		GPSMsToW = weekday * 86400000 + time.hour * 3600000 + time.minute * 60000 + time.second * 1000
		return GPSMsToW		

	"""Input units: ms, cm/s, cm/s, cm/s, cm/s, cm/s, deg, cm/s, deg"""
	def sendNAV_VELNED(self, GPSMsToW, velN, velE, velD, speed, gSpeed, heading, sAcc, headingAcc):
		msg = struct.pack('<cccchLlllLLlLL', self.SYNC[0], self.SYNC[1], self.NAV_VELNED[0], self.NAV_VELNED[1], 36, GPSMsToW, velN, velE, velD, speed, gSpeed, heading, sAcc, cAcc)
		msg += self.checksum(msg[2:])
		self.ser0.write(msg)

	"""Input units: ms, deg, deg, mm, mm, mm, mm"""
	def sendNAV_POSLLH(self, GPSMsToW, lat, lon, height, hMSL, hAcc, vAcc): #Can GPSMsToW just be a constant?
		msg = struct.pack('<cccchLllllLL', self.SYNC[0], self.SYNC[1], self.NAV_POSLLH[0], self.NAV_POSLLH[1], 28, GPSMsToW, lon * 10000000, lat * 10000000, height, hMSL, hAcc, vAcc)
		msg += self.checksum(msg[2:])
		self.ser0.write(msg)
	
	"""Input units: ms"""
	def sendNAV_DOP(self, GPSMsToW, gDOP, pDOP, tDOP, vDOP, hDOP, nDOP, eDOP):
		msg = struct.pack('<cccchLHHHHHHH', self.SYNC[0], self.SYNC[1], self.NAV_DOP[0], self.NAV_DOP[1], 18, GPSMsToW, gDOP * 100, pDOP * 100, tDOP * 100, vDOP * 100, hDOP * 100, nDOP * 100, eDOP * 100)
		msg += self.checksum(msg[2:])
		self.ser0.write(msg)
	
	"""Input units: ns, ns, year, month, day, hour, minute, second"""
	def sendNAV_TIMEUTC(self, GPSMsToW, tAcc, nano, year, month, day, hour, minute, sec, valid):
		msg = struct.pack('<cccchLLlHhhhhhc', self.SYNC[0], self.SYNC[1], self.NAV_TIMEUTC[0], self.NAV_TIMEUTC[1], 20, GPSMsToW, tAcc, nano, year, month, day, hour, minute, sec, valid)
		msg += self.checksum(msg[2:])
		self.ser0.write(msg)
	

spoof = UBXSpoofer()
spoof.startSpoofing()

"""
	def readMessagesStream(self):
		readByte = self.ser0.read()
		while True:
			if readByte == "\xb5":
				print "----------NEW MESSAGE----------"
				print hex(ord(readByte))
				readAndPrint(self.ser0)
				print "-----------CLASS & ID----------"
				readAndPrint(self.ser0)
				readAndPrint(self.ser0)
				print "------------LENGTH-------------"
				readAndPrint(self.ser0)
				readAndPrint(self.ser0)
				print "------PAYLOAD & CHECKSUM-------"
				readByte = self.ser0.read() #Reads startbyte of next package
				while readByte != "\xb5":
					print hex(ord(readByte))
					readByte = self.ser0.read()
				print "----------MESSAGE END----------"
			else:
				readByte = self.ser0.read()
				print hex(ord(readByte))
				
	def classify(self):
		readByte = ""
		while readByte != "\xb5":
			readByte = self.ser0.read()
		readByte = self.ser0.read()
		self.messageClass = self.ser0.read()
		self.messageID = self.ser0.read()
		print "----------Message classified-----------"
		print "messageClass: ", hex(ord(self.messageClass))
		print "messageID: ", hex(ord(self.messageID))

	def sendACK(self):
		MSG = ""
		self.ser0.write(struct.pack('c', b"\xb5"))
		self.ser0.write(struct.pack('c', b"\x62"))
		self.ser0.write(struct.pack('c', b"\x05"))
		MSG = struct.pack('c', b"\x05")
		self.ser0.write(struct.pack('c', b"\x01"))
		MSG += struct.pack('c', b"\x01")
		self.ser0.write(struct.pack('<h', 2))
		MSG += struct.pack('<h', 2)
		self.ser0.write(struct.pack('c', self.messageClass))
		MSG += struct.pack('c', self.messageClass)
		self.ser0.write(struct.pack('c', self.messageID))
		MSG += struct.pack('c', self.messageID)
		A, B = self.checksum(MSG)
		self.ser0.write(A)
		self.ser0.write(B)
		print "ACK sent"
"""
