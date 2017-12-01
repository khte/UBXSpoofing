"""
uBlox UBX protocol spoofer for AutoQuad

Author: Kristian Husum Terkildsen, khte@mmmi.sdu.dk

Notes to dev:
* make port a part of class init, no reason for it to be a variable, as it will never change.
* Test GPS module outside

Sources of inspiration:
* https://github.com/deleted/ublox/blob/master/message.py
"""

import serial
import struct
import time

ser0 = serial.Serial(port = "/dev/ttyUSB0") #, baudrate = 9600)


def readAndPrint(port):
	readByte = port.read()
	print hex(ord(readByte))
	return readByte
"""
def dontCareJustListen(port):
	positionMSG = struct.pack("cccchLllllLL", b"\xb5", b"\x62", b"\x01", b"\x02", 28, 10000000, 0.000001043, 0.000005537, 10000, 10000, 100, 100)
	positionMSG += checksum(positionMSG[2:])
	while True:
		port.write(positionMSG)
"""

class UBXSpoofer():
	def __init__(self):
		#UBX header and ID's
		#self.SYNC = b"\xb5\x62"
		#self.CFG_PRT = b"\x06\x00"
		#self.ACK_ACK = b"\x05\x01"
		#self.NAV_POSLLH = b"\x01\x02"
		self.checksumA = 0
		self.checksumB = 0
		self.messageClass = ""
		self.messageID = ""

	
	def checksum(self, message):
		CK_A = 0x00
		CK_B = 0x00
		buf = buffer(message)
		for i in buf:
			CK_A += ord(i) #Return integer value representing the character
			#CK_A &= 255 #REMOVE MASK??
			CK_B += CK_A
			#CK_B &= 255 #REMOVE MASK??
		print "CK_A: ", CK_A
		print "CK_B: ", CK_B
		return struct.pack('B', CK_A), struct.pack('B', CK_B)
	
	
	def checksumClear(self):
		self.checksumA = 0
		self.checksumB = 0
	
	def checksumCalc(self, char):
		self.checksumA += ord(char) #Should input be 0x00 instead of b"\x00"???
		self.checksumB += self.checksumA
	
	def readMessagesStream(self, port):
		readByte = port.read()
		while True:
			if readByte == "\xb5":
				print "----------NEW MESSAGE----------"
				print hex(ord(readByte))
				readAndPrint(port)
				print "-----------CLASS & ID----------"
				readAndPrint(port)
				readAndPrint(port)
				print "------------LENGTH-------------"
				readAndPrint(port)
				readAndPrint(port)
				print "------PAYLOAD & CHECKSUM-------"
				readByte = port.read() #Reads startbyte of next package
				while readByte != "\xb5":
					print hex(ord(readByte))
					readByte = port.read()
				print "----------MESSAGE END----------"
			else:
				readByte = port.read()
				print hex(ord(readByte))
				

	def classify(self, port):
		readByte = ""
		while readByte != "\xb5":
			readByte = port.read()
		readByte = port.read()
		self.messageClass = port.read()
		self.messageID = port.read()
		print "----------Message classified-----------"
		print "messageClass: ", hex(ord(self.messageClass))
		print "messageID: ", hex(ord(self.messageID))

	def sendACK(self, port):
		#self.checksumClear()
		port.write(struct.pack('c', b"\xb5"))
		port.write(struct.pack('c', b"\x62"))
		port.write(struct.pack('c', b"\x05"))
		#self.checksumCalc(b"\x05")
		MSG = struct.pack('c', b"\x05")
		port.write(struct.pack('c', b"\x01"))
		#self.checksumCalc(b"\x01")
		MSG += struct.pack('c', b"\x01")
		port.write(struct.pack('c', b"\x02")) #Little
		#self.checksumCalc(b"\x02")
		MSG += struct.pack('c', b"\x02")
		port.write(struct.pack('c', b"\x00")) #	endian
		#self.checksumCalc(b"\x00")
		MSG += struct.pack('c', b"\x00")
		port.write(struct.pack('c', b"\x06")) #Maybe try c
		#self.checksumCalc(b"\x06")
		MSG += struct.pack('c', b"\x06")
		port.write(struct.pack('c', b"\x00")) #Maybe try c
		#self.checksumCalc(b"\x00")
		MSG += struct.pack('c', b"\x00")
		A, B = self.checksum(MSG)
		port.write(A)
		port.write(B)
		#port.write(struct.pack('B', self.checksumA)) #Maybe try c
		#port.write(struct.pack('B', self.checksumB)) #Maybe try c
		
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
		port.write(ACKMessage)
		port.write("\r\n")
		"""
		print "ACK sent"

test = UBXSpoofer()
#while True:
#	test.classify(ser0)
#	test.sendACK(ser0)
test.readMessagesStream(ser0)


