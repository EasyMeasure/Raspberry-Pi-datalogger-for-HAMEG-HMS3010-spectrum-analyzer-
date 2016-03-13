#!/usr/bin/python

# Mateo Mayer
# EasyMeasure B.V.
# Breestraat 22
# 3811 BJ Amersfoort
# The Netherlands
# www.easymeasure.nl
# March 2016

# License info: GNU General Public License
# see Github, user EasyMeasure

# code snippet for automation of logging frequency sweeps with a HAMEG HMS3010
# spectrum analyzer with tracking generator using a Raspberry Pi as data logger
# Notes:
# - just an unoptimized snippet that did the job for a specific application
# - the pyserial communication module is used
# - a commercially available USB cable with FTDI chip and RS232 connector is used
# to connect the Raspberry Pi with the HAMEG HMS3010

import serial
import time
import numpy as num
import numpy.matlib as M
from numpy.matlib import rand,zeros,ones,empty,eye
import csv
import os

# the pyserial communication was gratefully derived from examples at stackoverflow.com
# At the HAMEG HMS3010, the setup button was pressed, RS232 was selected and after
# pushing the parameters button, the baudrate was set at 2400, stopbits at 1, 
# parity at none, handshake at none and these settings were saved on the HAMEG device
# Before starting logging, it is recommended to restart the HAMEG HMS3010 and to switch
# on the tracking generator by pushing the freq button and selecting track gen on

# see also stackoverflow.com, below some notes are given 
# 1. None: wait forever, block call
# 2. 0: non-blocking mode, return immediately
# 3. x, x is bigger than 0, float allowed, timeout block call
ser = serial.Serial()
#ser.port = "/dev/ttyUSB0"
ser.port = "/dev/ttyUSB0"
#ser.port = "/dev/ttyS2"
ser.baudrate = 2400 # higher baudrates than 2400 sometimes resulted in communication problems
# with the HAMEG device. This baudrate issue was not further investigated since logging speed was ok
# in the application the code snippet was used for.
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 1     #timeout for write

try:
    ser.open()
except Exception, e:
    #print "error opening serial port"
    exit()
if ser.isOpen():
    time.sleep(1) # wait 1 second before starting the communication
    ser.flushInput() #clears all buffers so that no garbage is read or send
# note that it may be required to switch on and off the HAMEG device before
# starting your data logging session
    while ser.isOpen():
# set the start frequency in Hz, in this example it is 1e8 meaning 100 MHz
# note that the HAMEG refuses to set the start frequency in case the start
# frequency is higher than the stop frequency. So it may be required that you
# set the stop frequency first at a higher value manually on the device or in 
# this code snippet by defining the stop frequency first.
        rs232_start_freq = "FREQ:STAR 1e8 MIN\n"
        ser.write(rs232_start_freq)
        dummy1=ser.readline()
# set the stop frequency in Hz, in this example it is 2e8 meaning 200 MHz
        rs232_stop_freq = "FREQ:STOP 2e8 MIN\n"
        ser.write(rs232_stop_freq)
        dummy2=ser.readline()
# send request for the date to the HAMEG spectrum analyzer        
        rs232_date = "SYSTEM:DATE?\n"
        ser.write(rs232_date)
# read the date that was sent by the HAMEG spectrum analyzer to the Raspberry Pi
        HAMEG_date = ser.readline()
# send request for the time to the HAMEG spectrum analyzer         
        rs232_time ="SYSTEM:TIME?\n"
        ser.write(rs232_time)
# read the time that was sent by the HAMEG spectrum analyzer to the Raspberry Pi        
        HAMEG_time = ser.readline()
# put the date and the time in the right format for writing it to a CSV file
# make one string for date HAMEG_date_CSV with the format yyyy-dd-hh
        HAMEG_date_CSV=""
        i=0
        while i < len(HAMEG_date):
            help_var=HAMEG_date[i]
            if help_var == ",":
              HAMEG_date_CSV=HAMEG_date_CSV + "-"
            if help_var <> "," and help_var <> "\n":
              HAMEG_date_CSV=HAMEG_date_CSV + help_var  
            i=i+1
# make one string for time HAMEG_time_CSV with the format hh-mm-ss
        HAMEG_time_CSV=""
        i=0
        while i < len(HAMEG_time):
            help_var=HAMEG_time[i]
            if help_var == ",":
              HAMEG_time_CSV=HAMEG_time_CSV + "-"
            if help_var <> "," and help_var <> "\n":
              HAMEG_time_CSV=HAMEG_time_CSV + help_var  
            i=i+1
# now make an amplitude versus frequency plot using the HAMEG trace data command
# send the request for the trace data to the HAMEG spectrum analyzer
        rs232_trace = "TRACE:DATA?\n"
        ser.write(rs232_trace)
# first read the dummy line and 2 column titles and flush them
# note that different HAMEG HMS3010 devices may have a slightly different number of dummy
# lines or column titles, so you might need to flush more or less lines, you'll have to check
# that with your particular device. Of course a lot of code optimization can be done here but the
# snippet just worked fine for the envisaged application
        i=1
        while (i <= 3):
         flush=ser.readline()
         i=i+1
#        print flush
# Open the csv file for writing the output data to a memory stick
# note here that in old Rpi Raspbian versions, the default directory is /media/name
# where name is the name of the memory stick whereas in recent versions the default
# directory is /media/pi/name
#         c=csv.writer(open('HAMEG_data.csv', 'a', 0))
        c=open('/media/pi/EasyMeasure/HAMEG_data1.csv', 'a', 0) # for a memory stick called EasyMeasure 
# the a stands for append and 0 is to set the buffer to zero
        j=1
        while j < 1002:
           AF=ser.readline()
           AF_CSV=""
           i=0
           while i < len(AF):
             help_var=AF[i]
             if help_var <> "\n":
               AF_CSV=AF_CSV + help_var  
             i=i+1
# flush the dummy character after the amplitude
#           AF_CSV=AF_CSV[0:(len(AF_CSV)-1)]
#           print AF_CSV
           data_row_CSV=HAMEG_date_CSV+","+HAMEG_time_CSV+","+AF_CSV
           length=len(data_row_CSV)-1
           data_row_CSV=data_row_CSV[0:length]
           data_row_CSV=data_row_CSV+"\n"
           c.write(data_row_CSV)
#           print data_row_CSV
           j=j+1            
        c.close()
#       ser.close()
        time.sleep(10) # just wait 10 seconds, here you can set the measuring frequency
# note that the time.sleep command is required to avoid timing issues between 2 frequency sweeps
        print "ready with a frequency sweep"
        ser.flushInput() #clears all buffers so that no garbage is read or send
else:
    print "cannot open serial port "
print "done!"
