import struct
import os

# Parameter
archive = "etalon.mview"

def readCString(f):
	"""This is the most naive implementation possible, don't use in prod"""
	str = ""
	c = f.read(1)
	while c != '\0':
		str += c
		c = f.read(1)
	return str

def getFileSize(f):
	pos = f.tell()
	f.seek(0, 2)
	end = f.tell()
	f.seek(pos, 0)
	return end

# Create the output directory
directory = os.path.splitext(archive)[0]
if not os.path.exists(directory):
    os.makedirs(directory)

with open(archive, 'rb') as f:
	end = getFileSize(f)
	while True:
		name = readCString(f)
		mime = readCString(f)
		compressed, size, rawSize = struct.unpack("III", f.read(3*4))
		if compressed:
			name += ".compressed"
		name = os.path.join(directory, name)
		print(name)
		with open(name, 'wb') as outf:
			outf.write(f.read(size))

		if f.tell() >= end:
			break
