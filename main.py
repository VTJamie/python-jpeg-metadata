import sys
import struct
import os
sys.path.append("src")

def seekToExif(f):
    for curbyte in iter(lambda: f.read(1), b''):
        if curbyte == b'\xFF':
            nextval = f.read(1)
            if nextval == b'\xE1':
                print("Found EXIF header")
                return True
    print("No EXIF Header")
    return False


def getExifInfo(f):
    exifsize, byteordermarker  = struct.unpack('<H6x2s2x', f.read(12))
    littleendian = byteordermarker == "II"
    endianstr = '<' if littleendian else '>'
    offsettotiff, = struct.unpack('{}I'.format(endianstr), f.read(4))
    f.read(offsettotiff-8)

    return (exifsize, endianstr)

with open('test.jpg', 'rb') as imagefile:
    if seekToExif(imagefile):
        headsize, endianchar = getExifInfo(imagefile)

        numberofitems, = struct.unpack('{}H'.format(endianchar), imagefile.read(2))

        print(numberofitems)
        for i in range(0, 1):
            typeval, formatval, numberofcomponents, offsettovalue = struct.unpack('{}HHII'.format(endianchar), imagefile.read(12))
            print('{:02x} {:02x} {} {}'.format(typeval, formatval, numberofcomponents, offsettovalue))
