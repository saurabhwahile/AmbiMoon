import serial
import time
import datetime
import json
import numpy
import pytz
from collections import OrderedDict

port = serial.Serial('COM11')
port.baudrate = 9600
NO_OF_LEDS = 43
LED_CORRECTION_OFFSET = 2
TIMEZONE = 'Asia/Kolkata'

class RGB():
  r = 0
  g = 0
  b = 0
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __str__(self):
    return str(self.r)+' '+str(self.g)+' '+str(self.b)

HOUR_COLOR = RGB(255,0,0)
MINUTE_COLOR = RGB(0,255,0)

clock_map = OrderedDict({
  0:    [11, 32],
  0.5:  [10, 31],
  1:    [30, 8],
  1.5:  [8, 29],
  2:    [7],
  2.5:  [28, 6],
  3:    [27, 5],
  3.5:  [26, 4],
  4:    [25, 3],
  4.5:  [24],
  5:    [23, 2],
  5.5:  [22, 1],
  6:    [21, 0],
  6.5:  [42],
  7:    [41, 20],
  7.5:  [40, 19],
  8:    [39, 18],
  8.5:  [17],
  9:    [38, 16],
  9.5:  [37],
  10:   [36, 15],
  10.5: [35, 14],
  11:   [34, 13],
  11.5: [33, 12],
})

leds = [RGB(0,0,0) for i in range(NO_OF_LEDS)]

def rotate_clock_map():
  global clock_map
  old_data = clock_map[0]
  for i in numpy.arange(0, 11.5, 0.5):
    clock_map[i] = clock_map[i+0.5]
  clock_map[11.5] = old_data 
  clock_map = OrderedDict(sorted(clock_map.iteritems()))

for i in range(LED_CORRECTION_OFFSET):
  rotate_clock_map()


def min2hr(min):
  return (min/59.0)*11.0

def dec2hex(dec):
  if dec < 16:
    return ('0'+str(hex(dec)).split('x')[1]).decode('hex')
  return str(hex(dec)).split('x')[1].decode('hex')

def distance(a, b):
  sub = a-b
  if sub < 0:
    return 1
  return sub

def start_frame():
  port.write(b'\x41\x64\x61\x00\x18\x4D')

def write_led_data():
  start_frame()
  for led in leds:
    port.write(dec2hex(led.r))
    port.write(dec2hex(led.g))
    port.write(dec2hex(led.b))

def get_time():
  return datetime.datetime.now(pytz.timezone(TIMEZONE))

def set_rgb_time__monochrome(t):
  for key, value in clock_map.iteritems():
    if key >= int(t.strftime('%I')):
      for led in value:
        leds[led] = RGB(255, 255, 255)
    if key <= min2hr(t.minute):
      for led in value:
        leds[led] = RGB(0, 0, 0)

def set_rgb_time__rgb(t, hrgb, mrgb):
  for key, value in clock_map.iteritems():
    if key >= 9:
      for led in value:
        leds[led] = RGB(255, 255, 255)
    else:
      for led in value:
        leds[led] = RGB(0, 0, 0)

def set_rgb_time__predef(t):
  flip = True
  for key, value in clock_map.iteritems():
    if distance(float(t.strftime('%I')), float(key)) < 0.5:
      flip = not flip
    if distance(min2hr(t.minute), float(key)) < 0.5:
      flip = not flip

    for led in value:
      if flip:
        leds[led] = HOUR_COLOR
      else:
        leds[led] = MINUTE_COLOR
      if distance(min2hr(t.second), float(key)) < 0.5:
        leds[led] = RGB(0, 0, 255)

while True:
  set_rgb_time__predef(get_time())
  write_led_data()

port.close()