import sys
import struct
from collections import namedtuple
import binascii
import os
sys.path.append("src")

IDFEntry = namedtuple('IDFEntry', 'tagval typeval numberofcomponents offsetorval')
testfile="test2.jpg"


def seekToExif(f):
    exifoffset = 6
    for curbyte in iter(lambda: f.read(1), b''):
        exifoffset += 1
        if curbyte == b'\xFF':
            nextval = f.read(1)
            exifoffset += 1
            if nextval == b'\xE1':
                exifoffset += 1
                print("Found EXIF header")
                return exifoffset
    print("No EXIF Header")
    return exifoffset



def getExifInfo(f):
    exifsize, byteordermarker  = struct.unpack('<H6x2s2x', f.read(12))
    littleendian = byteordermarker == "II"
    endianstr = '<' if littleendian else '>'
    offsettotiff, = struct.unpack('{}I'.format(endianstr), f.read(4))
    print('Offset To Tiff: {}'.format(offsettotiff))
    f.read(offsettotiff-8)

    return (exifsize, endianstr)

def loadIDFEntries(f, idflist, endianchar):
    numberofitems, = struct.unpack('{}H'.format(endianchar), imagefile.read(2))
    print(numberofitems)
    for i in range(0, numberofitems):
        tagval, typeval, numberofcomponents, offsetorval = struct.unpack('{}HHII'.format(endianchar), f.read(12))
        curval = IDFEntry(tagval=tagval, typeval=typeval, numberofcomponents=numberofcomponents, offsetorval=offsetorval)
        idflist.append(curval)


def loadGPSIDFEntries(f, idflist):
    numberofitems, = struct.unpack('>Hx', imagefile.read(3))
    print(numberofitems)
    for i in range(0, numberofitems):
        #curloc = f.tell()
        #print('{} {}'.format(curloc, binascii.hexlify(f.read(12))))
        tagval, typeval, numberofcomponents, offsetorval = struct.unpack('<HHII', f.read(12))

        curval = IDFEntry(tagval=tagval, typeval=typeval, numberofcomponents=numberofcomponents, offsetorval=offsetorval)
        idflist.append(curval)

def processExifIDFEntries(f, idflist, gpslist, endianchar, offset):
    for i in idflist:
        if i.tagval == 0x010f:
            imagefile.seek(i.offsetorval+offset)
            print('MAKE: {}'.format(imagefile.read(i.numberofcomponents).decode('ascii')))
        elif i.tagval == 0x0110:
            imagefile.seek(i.offsetorval+offset)
            print('MODEL: {}'.format(imagefile.read(i.numberofcomponents).decode('ascii')))
        elif i.tagval == 0x0131:
            imagefile.seek(i.offsetorval+offset)
            print('FIRMWARE: {}'.format(imagefile.read(i.numberofcomponents).decode('ascii')))
        elif i.tagval == 0x8769:
            print('Offset to SubExif: {}'.format(i.offsetorval))
        elif i.typeval == 0x0002:
            imagefile.seek(i.offsetorval+offset)
            print('{:04x}: {}'.format(i.tagval, imagefile.read(i.numberofcomponents).decode('ascii')))
        elif i.tagval == 0x8825:
            print('GPS Offset {}'.format(i.offsetorval + offset))
            imagefile.seek(i.offsetorval+offset)
            loadGPSIDFEntries(f, gpslist)
       # else:
            #print('{:04x}'.format(i.tagval))


def processGPSIDFEntries(f, gpslist, offset):
    print('GPS IDF')
    for i in gpslist:
        if i.tagval == 0x0001:
            print('{:04x}: GPSLatitudeRef {} {}'.format(i.tagval, chr(i.offsetorval), '-' if chr(i.offsetorval) == 'S' else '+'))
        elif i.tagval == 0x0002:
            print('{:04x}: Latitude: {}'.format(i.tagval, i.offsetorval+offset))
            f.seek(i.offsetorval+offset+1)
            dnum, dden = struct.unpack('<II', f.read(8))
            mnum, mden = struct.unpack('<II', f.read(8))
            snum, sden = struct.unpack('<II', f.read(8))

            dval = float(dnum)/float(dden)
            mval = float(mnum)/float(mden)
            sval = float(snum)/float(sden)
            decimaldegrees = dval + mval/60 + sval/3600
            print('Latitude: {} {} {} {}'.format(dval, mval, sval, decimaldegrees))
        elif i.tagval == 0x0003:
            print('{:04x}: GPSLongitudeRef {} {}'.format(i.tagval, chr(i.offsetorval), '-' if chr(i.offsetorval) == 'W' else '+') )
        elif i.tagval == 0x0004:

            f.seek(i.offsetorval+offset+1)
            dnum, dden = struct.unpack('<II', f.read(8))
            mnum, mden = struct.unpack('<II', f.read(8))
            snum, sden = struct.unpack('<II', f.read(8))
            dval = float(dnum)/float(dden)
            mval = float(mnum)/float(mden)
            sval = float(snum)/float(sden)
            decimaldegrees = dval + mval/60 + sval/3600
            print('Longitude: {} {} {} {}'.format(dval, mval, sval, decimaldegrees))
        elif i.tagval == 0x0005:
            print('{:04x}: GPSAltitudeRef {}'.format(i.tagval, i.offsetorval) )
        elif i.tagval == 0x0006:
            #print('{:04x}: GPSAltitude {}'.format(i.tagval, i.offsetorval+offset))
            f.seek(i.offsetorval+offset)
            num, den = struct.unpack('<II', f.read(8))
            print('GPSAltitude: {}'.format(float(num)/den))
        else:
            print('{:04x}'.format(i.tagval))
        #print('{:04x}'.format(i.tagval))

exifentries = []
gpsentries = []

with open(testfile, 'rb') as imagefile:
    exiflocation = seekToExif(imagefile)
    print('Exif Location: {}'.format(exiflocation))
    if exiflocation:
        headsize, endianchar = getExifInfo(imagefile)
        loadIDFEntries(imagefile, exifentries, endianchar)
        processExifIDFEntries(imagefile, exifentries, gpsentries, endianchar, exiflocation)

        processGPSIDFEntries(imagefile, gpsentries, exiflocation)