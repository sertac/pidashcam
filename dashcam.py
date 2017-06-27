import subprocess
import pynmea2
import sys
import os
from time import sleep
import datetime as dt

proc = subprocess.Popen("/usr/bin/gpspipe -r",stdout=subprocess.PIPE,shell=True)
time=lat_dir=lon_dir=""
lat=lon=speed=alt=speed=0.0
s,lat_err,lon_err,alt_err="","","",""


import picamera
import datetime as dt

camera = picamera.PiCamera(resolution=(1920,1080), framerate=30)
camera.start_preview()
camera.annotate_background = None
camera.annotate_text_size = 22

MAX_DISK_USAGE=90
VIDEO_LEN=300 #5 mins

global start
camera.start_recording('0.h264')
start = dt.datetime.now()
camera.wait_recording(0.1)

global i,reset

reset=False

files=[]
import glob
os.chdir("/home/pi/camera/")
for file in glob.glob("*.h264"):
    files.append(int(file.split('.')[0]))

if files:
  i=max(files)
else:
  i=0

import itertools
for j in itertools.count():
  free=int(subprocess.Popen(["df", "-Pk", "/home/pi/camera"], stdout=subprocess.PIPE).communicate()[0].splitlines()[1].split()[4][:2])

  if free>MAX_DISK_USAGE and reset==False:
     reset=True
     i=1
 # else:
 #    i=i+1

  line = proc.stdout.readline()
  rline=line.rstrip()
  #print rline

  if rline[:6]=="$GPZDA":
     time=pynmea2.parse(rline).datetime
     #print time

  #if rline[:6]=="$GPGSA":
  #   mode_fix_type=pynmea2.parse(rline).mode_fix_type

  if rline[:6]=="$GPRMC":
     speed=float(pynmea2.parse(rline).spd_over_grnd)*1.852

  if rline[:6]=="$GPGGA":
     msg=pynmea2.parse(rline)
     lat=msg.lat
     lat_dir=msg.lat_dir
     lon=msg.lon
     lon_dir=msg.lon_dir
     alt=msg.altitude

  if rline[:6]=="$GPGBS":
     msg=rline.split(',')
     lat_err=msg[4]
     lon_err=msg[2]
     alt_err=msg[6]

  s="Time: %s\nLatitude: %.2f %s (+/- %s)\nLongitude: %.2f %s (+/- %s)\nAltitude: %.2f m (+/- %s)\nSpeed: %.1f km/h" % \
        (time,float(lat),lat_dir,lat_err,float(lon),lon_dir,lon_err,float(alt),alt_err,speed)

  camera.annotate_text = s
  camera.wait_recording(0.2)

  if (dt.datetime.now()-start).total_seconds() >= VIDEO_LEN:
      camera.split_recording('%d.h264' % i)
      start=dt.datetime.now()
      i=i+1
      print "recording now %d" % i
#camera.stop_recording()
