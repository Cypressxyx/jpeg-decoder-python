import time
from LexicalAnalayzer import LexicalAnalayzer
from HuffmanTable import HuffmanTable
from QuantizeTable import QuantizeTable
lookup_dc = {
    1: 1,
    2: 3,
    3: 7,
    4: 15,
    5: 31,
    6: 63,
    7: 127,
    8: 255,
    9: 511,
    10: 1023,
    11: 2047
}
w1 = 2841 # 2048*sqrt(2)*cos(1*pi/16)
w2 = 2676 # 2048*sqrt(2)*cos(2*pi/16)
w3 = 2408 # 2048*sqrt(2)*cos(3*pi/16)
w5 = 1609 # 2048*sqrt(2)*cos(5*pi/16)
w6 = 1108 # 2048*sqrt(2)*cos(6*pi/16)
w7 = 565  # 2048*sqrt(2)*cos(7*pi/16)
w1pw7 = w1 + w7
w1mw7 = w1 - w7
w2pw6 = w2 + w6
w2mw6 = w2 - w6
w3pw5 = w3 + w5
w3mw5 = w3 - w5
r2 = 181

def idct(table):
	b1 = [0 for i in range(1,65)]
	b1[0] = table[0]

	b2 = [0 for i in range(1,65)]
	b2[0] = table[1]

	imageTable =[]

	#idct row
	for i in range(0,8):
		pos = i * 8
		dc = b1[pos] << 3
		b1[pos] = dc
		b1[pos + 1] = dc
		b1[pos + 2] = dc
		b1[pos + 3] = dc
		b1[pos + 4] = dc
		b1[pos + 5] = dc
		b1[pos + 6] = dc
		b1[pos + 7] = dc

	for i in range(0,8):
		pos = i * 8
		dc = (b1[pos ] << 8) + 8192
		b1[pos] = dc
		b1[pos + 1] = dc
		b1[pos + 2] = dc
		b1[pos + 3] = dc
		b1[pos + 4] = dc
		b1[pos + 5] = dc
		b1[pos + 6] = dc
		b1[pos + 7] = dc
	#print(b1)

	return imageTable

def decodeQuantTable(stream):
	quantTable = []	
	stream = stream[2:]
	while(len(stream) > 0):
		quantTable.append(stream[0])
		stream = stream[1:]
	return quantTable

def getRelative(table):
	table[1] = table[1] + table[0]
		
def numSize(num):
	cnt = 1
	while int(num / 2) != 0:
		cnt += 1
		num = num / 2
	return cnt

def print_image(bytes):
	for byte in bytes:
		val = hex(byte)[2:]
		if val == "ff":
			print("----", end="")
		print(val, end=" ")

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
	for i in range (len(string)):
		if i % 4 == 0:
			output += " "
		output += string[i]
	return output

def  count_bits(n):
    count = 0
    while (n):
        count += n & 1
        n >>= 1
    return count


def decode_bits(bit_stream, hT, table, num_codes_length):
	if len(bit_stream) == 0:
		return []
	bit = bit_stream[0]
	bit_stream = bit_stream[1:]
	value = 0 if bit == "0" else 1
	length_to_move = None
	num_bits = 1
	while bit_stream:
		if num_codes_length[num_bits - 1] != 0:
			#check to see if encoding is in huffman table
			for key, v in hT.items():
				if key == value:
					length_to_move = v
					if v > 15:
						length_to_move = length_to_move & 0x0f # this is the highest smallest hex value aka 0f
					break
		if length_to_move != None:
			break
		bit = bit_stream[0]
		bit_stream = bit_stream[1:]
		if bit == "1":
			value = value << 1
			value = value | 1
		else:
			value = value << 1
		num_bits += 1

	#print("encoded value: " , val, " ", bin(encodeSize))
	if length_to_move == 0:
		'''
		print("EOB Found, exiting")
		print("remaining string: ", sString)
		'''
		bit_stream = "EOB" + bit_stream
		return bit_stream
	if length_to_move == None:
		print("hi")
		return  bit_stream

	bit = bit_stream[0]
	first_bit = bit
	bit_stream = bit_stream[1:]
	actual_value = 1 if bit == "1" else 0
	for i in range(length_to_move - 1):
		if len(bit_stream) == 0:
			break

		bit = bit_stream[0]
		bit_stream = bit_stream[1:]
		actual_value = (actual_value << 1) | 1 if bit == "1" else actual_value << 1

	if first_bit == "0":
		if length_to_move == 17:
			print("Wtf")
		actual_value = -1 * lookup_dc[length_to_move] + actual_value
		#actual_value = ~actual_value
	table.append(actual_value)
	return bit_stream

def decodeBits(sString, hT, table):
	#print(hT)
	prefix = sString[0]
	encodeSize = 0
	val = 0
	testStr = ""
	idx = 0
	for i in range(len(hT)):
		#print(prefix , " " , bin(hT[i][0])[2:], "i and idx:" , i ," ",idx)
		#print(mapping[i], " ",bin(mapping[i][0])[2:] ," ", prefix)
		if(hT[i][0] > int(prefix,2)):
			idx += 1
			prefix += sString[idx]
		if((hT[i][0]) == int(prefix,2)):
			idx += 1
			val = hT[i][1]
			encodeSize = hT[i][0]
			print("Found encoding: ", prefix," is ", val)
			if(val == 0):
				if(encodeSize == 1):
					encodeSize = 2
				break
			prefix += sString[idx]
			#shi	ft += 1
			#sPrefix = string << 0 & shift

	#remove from string
	print(sString)
	sString = sString[numSize(encodeSize):]
	print(sString)

	#print("encoded value: " , val, " ", bin(encodeSize))
	if val == 0:
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
	if testStr[len(testStr) - 1] == "1":
		value = ~value
	#print("Code value:", value, testStr)
	#print("bytestream length:", len(sString))
	sString = sString[val:] 
	#print("remaining string: ", sString)
	#print(" ")
	table.append(value)
	return sString


def decode_sos_stream(stream, huffman_mapping):
	mapping = huffman_mapping.get_table()
	all_code_lengths = huffman_mapping.get_code_lengths()
	table = []
	# get num componenets
	stream.pop(0)
	numComponents = stream.pop(0)

	# assign the huffman table for the compontents y cb cr
	# read 2 bytes at a time
	for i in range(numComponents):
		byteOne = stream.pop(0)
		byteTwo = stream.pop(0)
		dcNum = byteTwo >> 4  # high bits
		acNum = byteTwo & 15  # low bits
		acNum = 0
		dcNum = 0
		if byteOne == 1:
			print("saving y ht ")
			yAc = mapping[acNum + 1]
			yDc = mapping[dcNum]
			yAcCodeLength = all_code_lengths[acNum + 1]
			yDcCodeLength = all_code_lengths[dcNum]
		if byteOne == 2:
			# print("saving cb ht ")
			cbAc = mapping[acNum + 1]
			cbDc = mapping[dcNum]
			cbAcCodeLen = all_code_lengths[acNum + 1]
			cbDcCodeLen = all_code_lengths[dcNum]
		if byteOne == 3:
			# print("saving cr ht ")
			crAc = mapping[acNum + 2]
			crDc = mapping[dcNum]
			crAcCodeLen = all_code_lengths[acNum + 1]
			crDcCodeLen = all_code_lengths[dcNum]

	stream = stream[3:]  # have to ignore 3 usless bytes

	sString = ""
	# combine strings
	# string = 0
	# saving the bytes as a bit string, idx has been removed(aug 28)
	while len(stream):
		# size = numSize(stream[idx])
		# string = (string << size) | stream[idx]
		val = stream[0]
		sString += bin(val)[2:].zfill(8)
		# print(readBinary(sString),bin(stream[idx])[2:])
		#remove padding 0
		stream.pop(0)
		if val == 0xff:
			stream.pop(0)
	# print (readBinary(sString))
	# shift = 0
	# sPrefix = string << 0 & shift
	# y[1] has replaced mapping[i]
	# see if we can get the first dc value from y
	# aug 28 creating a new function that finds the encoding
	while len(sString):
		# luminance values(y)
		# print(" y ac and dc values")
		sString = decode_bits(sString, yDc, table, yDcCodeLength)
		if sString[:3] == "EOB":
			sString = sString[3:]
			table.append(0)
		for i in range(63):
			if (sString[:3] == "EOB"):
				sString = sString[3:]
				break
			sString = decode_bits(sString, yAc, [], yAcCodeLength)

		# chromiance cb values
		# print(" CB ac and dc values")
		if numComponents is not 1:
			sString = decode_bits(sString, cbDc, table, cbDcCodeLen)
			if (sString[:3] == "EOB"):
				sString = sString[3:]
			for i in range(0, 63):
				if (sString[:3] == "EOB"):
					sString = sString[3:]
					break
			sString = decode_bits(sString, cbAc, [], cbAcCodeLen)
			# chromiance cr values
			# print(" CR ac and dc values")
			sString = decode_bits(sString, crDc, table, crDcCodeLen)
			if (sString[:3] == "EOB"):
				sString = sString[3:]
			for i in range(0, 63):
				if (sString[:3] == "EOB"):
					sString = sString[3:]
					break
				sString = decode_bits(sString, crAc, [], crAcCodeLen)

		if len(sString) < 8:
			return table


def decodeSosStream(stream,mapping):
	table = []
	#get num componenets
	numComponents = stream[1]
	stream = stream[2:]

	#assign the huffman table for the compontents y cb cr 
	#read 2 bytes at a time
	for i in range(0, numComponents):
		byteOne = stream[0]
		byteTwo = stream[1]
		dcNum =  byteTwo >> 4 #high bits
		acNum = byteTwo & 15  #low bits
		if byteOne == 1:
			#print("saving y ht ")
			yAc = mapping[acNum + 2]
			yDc = mapping[dcNum]
		if byteOne == 2:
			#print("saving cb ht ")
			cbAc = mapping[acNum + 2]
			cbDc = mapping[dcNum]
		if byteOne == 3:
			#print("saving cr ht ")
			crAc = mapping[acNum + 2]
			crDc = mapping[dcNum]
		stream = stream[2:]

	stream = stream[3:]  # have to ignore 3 usless bytes per jpeg standard
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
			sString = decodeBits(sString, yAc, table)

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
	

def load_image(img_path):
	with open(img_path, 'rb') as image:
		img = image.read()
		#hex_content = image.read().encode('hex')

	return bytearray(img)

def convert_to_rgb(values):
	values = [value/4 for value in values]
	for value in values:
		value += 128
		red = value - 179.456
		green = value + 0.34414*128 + 0.71414* 128
		blue = value - 1.772 * 128
		print(red, green, blue)


def decode_jpeg(image_path):
	try:
		image_stream = load_image(image_path)
	except:
		exit("Could not find image. Exiting")
	#print_image(image_stream)
	analyzer = LexicalAnalayzer(image_stream.copy())

	""" get quantization stream """
	#quantStream = getMarker(image_stream, 0xdb, 0xff)
	quantize_stream = analyzer.get_marker(0xdb, 0xff)
	#print(quantize_stream) low bit and high bit

	""" get quantization table """
	#quantTable = decodeQuantTable(quantStream)
	quantize_table = QuantizeTable(quantize_stream)
	#print(quantTable)

	""" get sos """
	#analyzer.get_marker(0xc0, 0xff)

	""" get huffman stream """
	huffman_stream = analyzer.get_marker(0xc4, 0xff)
	#huffmanStream = getMarker(image_stream, 0xc4, 0xff)
	token_one, token_two = analyzer.get_next_two_tokens()
	while token_one == 0xff and token_two == 0xc4:
		huffman_stream.extend(analyzer.get_marker(0xc4, 0xff))
		token_one, token_two = analyzer.get_next_two_tokens()

	huffman_mapping = HuffmanTable(huffman_stream)
	#mapping = decodeHuffmanTable(huffmanStream)
	"""
	print("\n Huffman stream")
	#printHex(mapping)
	print(mapping)
	print("\n Huffman stream 2")
	print(huffman_mapping.get_table())
	print("done")
	"""
	sos_stream = analyzer.get_marker(0xda, 0xd9, 0xff)
	sosStream = getMarker(image_stream, 0xda, 0xd9)
	#removing the ff value
	sosStream = sosStream[:-1]
	#printHex(sosStream)
	sos_stream.pop(0)
	table_1 = decode_sos_stream(sos_stream, huffman_mapping)
	table_1 = convert_to_relative(table_1)
	table_1 = convert_to_image(table_1)
	image_to_plot = []
	table_1 = table_1[:2070]
	row = []
	img_height = 368
	img_width = 356
	print(len(table_1))
	for i in range(int(46)):
		col = []
		for j in range(int(45)):
			col.append(table_1[i * j + j ])
			print(table_1[i * j + j ])
		row.append(col)

	import numpy as np
	row = np.array(row, np.int32)
	import matplotlib.pyplot as plt
	plt.imshow(row, cmap="gray", )
	plt.show()
	x = 1

	#table = decodeSosStream(sosStream, mapping)
	#print(table)
	#getRelative(table)
	#getRelative(table_1)
	#values = convert_to_rgb(table)
	#print(table)
	#print(table_1)
	#table = idct(table)

def convert_to_image(table_1):
	x = []
	for value in table_1:
		rgb = value/8 + 128
		if rgb < 0:
			rgb = 0
		if rgb > 50:
			rgb = 255
		x.append([rgb, rgb, rgb])
	return x

def convert_to_relative(table):
	x = [table[0]]
	prev = table[0]
	for i in range(1, len(table)):
		actual_value = table[i] + prev
		x.append(actual_value)
		prev = actual_value
	return x

#decode_jpeg("8x8.jpg")
#decode_jpeg("test.jpg")
#decode_jpeg("t.jpg")
decode_jpeg("cas2.jpg")
