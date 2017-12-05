"""
uBlox UBX protocol spoofer for AutoQuad

Author: Kristian Husum Terkildsen, khte@mmmi.sdu.dk

Notes to dev: 
* Try other baud rates? 9600?
* Clean up file
* Add the other requested messages

Sources of inspiration:
* https://github.com/deleted/ublox/blob/master/message.py
"""

import serial
import struct
import time

def readAndPrint(port):
	readByte = port.read()
	print hex(ord(readByte))
	return readByte

class UBXSpoofer():
	def __init__(self):
		#UBX header and ID's
		self.SYNC = b"\xb5\x62"
		self.NAV_POSLLH = b"\x01\x02"
		#self.CFG_PRT = b"\x06\x00"
		#self.ACK_ACK = b"\x05\x01"
		#self.checksumA = 0
		#self.checksumB = 0
		self.ser0 = serial.Serial(port = "/dev/ttyUSB0", baudrate = 230400)
		self.messageClass = ""
		self.messageID = ""
	
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
		
		"""
		ACKMessage = struct.pack('cc', self.SYNC[0], self.SYNC[1])
		ACKMessage += struct.pack('cc', self.ACK_ACK[0], self.ACK_ACK[1])
		ACKMessage += struct.pack('<h', 2)
		if self.messageClass == "":
			print "not the correct message type"
		if self.messageClass == "\x06" and self.messageID == "\x00":
			print "correct message type"
			ACKMessage += struct.pack('BB', 0x06, 0x00)
		ACKMessage += self.checksum(ACKMessage[2:])
		self.ser0.write(ACKMessage)
		self.ser0.write("\r\n")
		"""
		print "ACK sent"

	def sendNAV_VELNED(self):
		MSG = ""
		self.ser0.write(struct.pack('c', b"\xb5")) #Change to sync from init
		self.ser0.write(struct.pack('c', b"\x62"))
		self.ser0.write(struct.pack('c', b"\x01"))
		MSG = struct.pack('c', b"\x01")
		self.ser0.write(struct.pack('c', b"\x12"))
		MSG = struct.pack('c', b"\x12")
		self.ser0.write(struct.pack('<h', 36))
		MSG = struct.pack('<h', 36)
		self.ser0.write(struct.pack('<L', 134644000))
		MSG = struct.pack('<L', 134644000)
		self.ser0.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		self.ser0.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		self.ser0.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		self.ser0.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		self.ser0.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		self.ser0.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		self.ser0.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		self.ser0.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		A, B = self.checksum(MSG)
		self.ser0.write(A)
		self.ser0.write(B)

	
	def sendNAV_POSLLH(self, GPSMsToW, lat, lon, height, hMSL, hAcc, vAcc): #Can GPSMsToW just be a constant?
		msg = struct.pack('<cccchLllllLL', self.SYNC[0], self.SYNC[1], self.NAV_POSLLH[0], self.NAV_POSLLH[1], 28, GPSMsToW, lon, lat, height, hMSL, hAcc, vAcc)
		msg += self.checksum(msg[2:])
		self.ser0.write(msg)
	
	#def sendNAV_DOP(self):
	
	#def sendNAV_TIMEUTC(self):
	

test = UBXSpoofer()

while True:
	test.sendNAV_POSLLH(134644000, 553666640, 104315760, 10000, 10000, 100, 100)

