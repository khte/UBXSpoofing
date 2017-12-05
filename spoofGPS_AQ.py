"""
uBlox UBX protocol spoofer for AutoQuad

Author: Kristian Husum Terkildsen, khte@mmmi.sdu.dk

Notes to dev:
* make port a part of class init, no reason for it to be a variable, as it will never change.
* I THINK AUTOQUAD USES MORE THAN JUST TX AND RX!! (TIMEPULSE, maybe not..)
* 
* Make sure that checksum is calculated correctly
* Try to send positions after receiving last conf. msg.
* Add the other requested messages
* What is rate in this case?
* Send with baud rate 9600?

Sources of inspiration:
* https://github.com/deleted/ublox/blob/master/message.py
"""

import serial
import struct
import time

ser0 = serial.Serial(port = "/dev/ttyUSB0", baudrate = 230400)

def readAndPrint(port):
	readByte = port.read()
	print hex(ord(readByte))
	return readByte

class UBXSpoofer():
	def __init__(self):
		#UBX header and ID's
		#self.SYNC = b"\xb5\x62"
		#self.CFG_PRT = b"\x06\x00"
		#self.ACK_ACK = b"\x05\x01"
		#self.NAV_POSLLH = b"\x01\x02"
		#self.checksumA = 0
		#self.checksumB = 0
		self.messageClass = ""
		self.messageID = ""


	def dontCareJustListen(self, port):
		#positionMSG = struct.pack("cccchLllllLL", b"\xb5", b"\x62", b"\x01", b"\x02", 28, 10000000, 0.000001043, 0.000005537, 10000, 10000, 100, 100) #Wrong, length is two bytes
		#positionMSG += self.checksum(positionMSG[2:])
		MSG = ""
		port.write(struct.pack('c', b"\xb5"))
		port.write(struct.pack('c', b"\x62"))
		port.write(struct.pack('c', b"\x01"))
		MSG = struct.pack('c', b"\x01")
		port.write(struct.pack('c', b"\x02"))
		MSG += struct.pack('c', b"\x02")
		port.write(struct.pack('<h', 28))
		MSG += struct.pack('<h', 28)
		port.write(struct.pack('<L', 134644000))
		MSG += struct.pack('<L', 134644000)
		port.write(struct.pack('<l', 0.000001043)) #Floating point??
		MSG += struct.pack('<l', 0.000001043)
		port.write(struct.pack('<l', 0.000005537))
		MSG += struct.pack('<l', 0.000005537)
		port.write(struct.pack('<l', 10000))
		MSG += struct.pack('<l', 10000)
		port.write(struct.pack('<l', 10000))
		MSG += struct.pack('<l', 10000)
		port.write(struct.pack('<L', 100))
		MSG += struct.pack('<L', 100)
		port.write(struct.pack('<L', 100))
		MSG += struct.pack('<L', 100)
		A, B = self.checksum(MSG)
		port.write(A)
		port.write(B)
		
		while True:
			port.write(MSG) #Misses header bytes..
	
	def checksum(self, message):
		CK_A = 0x00
		CK_B = 0x00
		buf = buffer(message)
		for i in buf:
			CK_A += ord(i) #Return integer value representing the character
			CK_A &= 255
			CK_B += CK_A
			CK_B &= 255
		return struct.pack('B', CK_A), struct.pack('B', CK_B)
	
	"""
	def checksumClear(self):
		self.checksumA = 0
		self.checksumB = 0
	
	def checksumCalc(self, char):
		self.checksumA += ord(char) #Should input be 0x00 instead of b"00"???
		self.checksumB += self.checksumA
	"""

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
		MSG = ""
		port.write(struct.pack('c', b"\xb5"))
		port.write(struct.pack('c', b"\x62"))
		port.write(struct.pack('c', b"\x05"))
		MSG = struct.pack('c', b"\x05")
		port.write(struct.pack('c', b"\x01"))
		MSG += struct.pack('c', b"\x01")
		port.write(struct.pack('<h', 2))
		MSG += struct.pack('<h', 2)
		port.write(struct.pack('c', self.messageClass))
		MSG += struct.pack('c', self.messageClass)
		port.write(struct.pack('c', self.messageID))
		MSG += struct.pack('c', self.messageID)
		A, B = self.checksum(MSG)
		port.write(A)
		port.write(B)
		
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

	def sendNAV_VELNED(self, port):
		MSG = ""
		port.write(struct.pack('c', b"\xb5"))
		port.write(struct.pack('c', b"\x62"))
		port.write(struct.pack('c', b"\x01"))
		MSG = struct.pack('c', b"\x01")
		port.write(struct.pack('c', b"\x12"))
		MSG = struct.pack('c', b"\x12")
		port.write(struct.pack('<h', 36))
		MSG = struct.pack('<h', 36)
		port.write(struct.pack('<L', 134644000))
		MSG = struct.pack('<L', 134644000)
		port.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		port.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		port.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		port.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		port.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		port.write(struct.pack('<l', 0))
		MSG = struct.pack('<l', 0)
		port.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		port.write(struct.pack('<L', 0))
		MSG = struct.pack('<L', 0)
		A, B = self.checksum(MSG)
		port.write(A)
		port.write(B)

	
	def sendNAV_POSLLH(self, port):
		MSG = ""
		MSG = struct.pack('c', b"\xb5")
		MSG += struct.pack('c', b"\x62")
		MSG += struct.pack('c', b"\x01")
		MSG += struct.pack('c', b"\x02")
		MSG += struct.pack('<h', 28)
		MSG += struct.pack('<L', 134644000)
		MSG += struct.pack('<l', 104315760)
		MSG += struct.pack('<l', 553666640)
		MSG += struct.pack('<l', 10000)
		MSG += struct.pack('<l', 10000)
		MSG += struct.pack('<L', 10)
		MSG += struct.pack('<L', 10)
		A, B = self.checksum(MSG[2:])
		MSG += A
		MSG += B
		
		port.write(MSG)
	
	#def sendNAV_DOP(self, port):
	
	#def sendNAV_TIMEUTC(self, port):
	

test = UBXSpoofer()
"""
while True:
	test.classify(ser0)
	test.sendACK(ser0)
"""
#test.readMessagesStream(ser0)
#test.dontCareJustListen(ser0)
test.sendNAV_POSLLH(ser0)

# 55.366664, 10.431576
# 553666640, 104315760
