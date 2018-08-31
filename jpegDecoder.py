import time
def idct(table):
	b1 = [0 for i in range(1,65)]
	b1[0] = table[0]

	b2 = [0 for i in range(1,65)]
	b2[0] = table[1]

	imageTable =[]

	#idct row
	for i in range(0,8):
		pos = 0;


	

	return imageTable
def getRelative(table):
	table[1] = table[1] + table[0]
		
def numSize(num):
	cnt = 1
	while(int(num / 2) != 0 ):
		cnt += 1
		num = num / 2
	return cnt

def printImage(b):
	for i in range(0,len(b)):
		val = hex(b[i])[2:]
		if(val == "ff"):
			print ("----",end="")
		print (val,end=" ")

def printHex(array):
	for i in range(0,len(array)):
		print( hex(array[i])[2:], end=" ")

def getMarker(stream,start,stop):
	search = True
	pos = 0
	byteStream = []
	while(search):
		if(stream[pos] == 0xff):
			if(stream[pos + 1] == start):
				search = False
		pos += 1

	pos += 2
	while( stream[pos] != stop):
		byteStream.append(stream[pos])
		pos += 1
	return byteStream

def decodeHuffmanTable(stream):
	hTabel = []
	#remove ht len
	stream = stream[2:]
	while(len(stream) > 0):
		#save first 16 code lengths, look into uint 16
		codeLens = []
		cnt = 0 
		for i in range(0,16):
			codeLens.append(stream[i])
			cnt += stream[i]

		stream = stream[16:]
		#save the code Values
		vals = []
		for i in range(0, cnt):
			vals.append(stream[i])
		stream = stream[cnt:]

		#map bits to values
		code = 0
		itr = 0
		mapping = []
		for i in range(0,len(codeLens)):
			for j in range(0, codeLens[i]):
				mapping.append([code,vals[itr]])
				itr += 1
				#print(bin(code))
				code += 1
			code <<= 1
		hTabel.append(mapping)
		stream = stream[1:] #remove ht type
	return hTabel

def readBinary(string):
	output = ""
	for i in range (0,len(string)):
		if(i % 4 == 0):
			output += " "
		output += string[i]
	return output


def decodeBits(sString,hT, table):
	#print(hT)
	prefix = sString[0]
	encodeSize = 0
	val = 0
	testStr = ""
	idx = 0
	for i in range(0,len(hT)):
		#print(prefix , " " , bin(hT[i][0])[2:], "i and idx:" , i ," ",idx)
		#print(mapping[i], " ",bin(mapping[i][0])[2:] ," ", prefix)
		if(hT[i][0] > int(prefix,2)):
			idx += 1
			prefix += sString[idx]
		if((hT[i][0]) == int(prefix,2)):
			idx += 1
			val = hT[i][1]
			encodeSize = hT[i][0]
			#print("Found encoding: ", prefix," is ", val)
			if(val == 0):
				if(encodeSize == 1):
					encodeSize = 2
				break
			prefix += sString[idx]
			#shi	ft += 1
			#sPrefix = string << 0 & shift

	#remove from string
	sString = sString[numSize(encodeSize):]

	#print("encoded value: " , val, " ", bin(encodeSize))
	if(val == 0):
		'''
		print("EOB Found, exiting")
		print("remaining string: ", sString)
		'''
		sString = "EOB" + sString
		#print(" ")
		return sString

	for i in range(0,val):
		testStr += sString[i]

	value = int(testStr,2)
	value = value
	if(testStr[len(testStr) - 1] == "1"):
		value = ~value
	#print("Code value:", value, testStr)
	#print("bytestream length:", len(sString))
	sString = sString[val:] 
	#print("remaining string: ", sString)
	#print(" ")

	#time.sleep(3)
	table.append(value)
	return sString

def decodeSosStream(stream,mapping):
	table = []
	#get num componenets
	numComponents = stream[1]
	stream = stream[2:]

	#assign the huffman table for the compontents y cb cr 
	#read 2 bytes at a time
	for i in range(0,numComponents):
		byteOne = stream[0]
		byteTwo = stream[1]
		dcNum =  byteTwo >> 4 #high bits
		acNum = byteTwo & 15  #low bits
		if(byteOne == 1):
			#print("saving y ht ")
			yAc = mapping[acNum + 2]
			yDc = mapping[dcNum]
		if(byteOne == 2):
			#print("saving cb ht ")
			cbAc = mapping[acNum + 2]
			cbDc = mapping[dcNum]
		if(byteOne == 3):
			#print("saving cr ht ")
			crAc = mapping[acNum + 2]
			crDc = mapping[dcNum]
		stream = stream[2:]

	stream = stream[3:]  #have to ignore 3 usless bytes

	sString = ""
	#combine strings
	#string = 0
	#saving the bytes as a bit string, idx has been removed(aug 28)
	while(len(stream) > 0):
		#size = numSize(stream[idx])
		#string = (string << size) | stream[idx]
		val = stream[0]
		sString += bin(val)[2:].zfill(8)
		#print(readBinary(sString),bin(stream[idx])[2:])
		if(val == 0xff):
			stream = stream[2:] #remove padding 0
		else:
			stream = stream[1:]

	#print (readBinary(sString))
	#shift = 0
	#sPrefix = string << 0 & shift
	prefix = sString[0]
	idx = 0
	
	#y[1] has replaced mapping[i]
	#see if we can get the first dc value from y
	#aug 28 creating a new function that finds the encoding
	while(len(sString) > 0):
		#luminance values(y)
		#print(" y ac and dc values")
		sString = decodeBits(sString,yDc, table)
		
		for i in range(0,63):
			if(sString[:3] == "EOB"):
				sString = sString[3:]
				break
			sString = decodeBits(sString,yAc,table)

		#chromiance cb values
		#print(" CB ac and dc values")
		sString = decodeBits(sString,cbDc,table)
		if(sString[:3] == "EOB"):
			sString = sString[3:]
		for i in range(0,63):
			if(sString[:3] == "EOB"):
				sString = sString[3:]
				break
			sString = decodeBits(sString,cbAc,table)

		#chromiance cr values
		#print(" CR ac and dc values")
		sString = decodeBits(sString,crDc,table)
		if(sString[:3] == "EOB"):
			sString = sString[3:]
		for i in range(0,63):
			if(sString[:3] == "EOB"):
				sString = sString[3:]
				break
			sString = decodeBits(sString,crAc,table)

		if(len(sString) < 8):
			return table
	#printHex(stream) 
	

def main():
	with open("8x8.jpg","rb") as image:
		file = image.read()
		imageStream = bytearray(file)
	#printImage(imageStream)
	huffmanStream = getMarker(imageStream,0xc4,0xff)
	mapping = decodeHuffmanTable(huffmanStream)
	#printHex(huffmanStream)

	sosStream = getMarker(imageStream,0xda,0xd9)
	#removing the ff value
	sosStream = sosStream[:-1]
	#printHex(sosStream)
	table = decodeSosStream(sosStream,mapping)
	getRelative(table)
	print(table)
	table = idct(table)



main()	
