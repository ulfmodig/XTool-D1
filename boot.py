# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#old: import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
#old: import gc
#import webrepl
#webrepl.start()
#old: gc.collect()

# Complete project details at https://RandomNerdTutorials.com

import time
from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import urequests
import os
import ujson
esp.osdebug(None)
import gc
gc.collect()

# Network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('modig', 'Dido88bole')
wlan_mac_address = ubinascii.hexlify(wlan.config('mac')).decode()
wlan_ip_address = wlan.ifconfig()[0]

# GIT Hub
github_user = "ulfmodig"
github_password = "LpQJdgB#s8&6AqD!"

# MQTT
mqtt_server = '192.168.1.90'

# GPIO
gpio_13_led = machine.Pin(13, machine.Pin.OUT)
gpio_12_relay = machine.Pin(12, machine.Pin.OUT)

while wlan.isconnected() == False:
  pass


