# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# old: import uos, machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
# old: import gc
import webrepl
webrepl.start()
# old: gc.collect()

# Complete project details at https://RandomNerdTutorials.com

import time
from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import urequests
import os
import ujson

import gc
gc.collect()

# Network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("modig", 'Dido88bole')
wlan_mac_address = ubinascii.hexlify(wlan.config('mac')).decode()
wlan_ip_address = wlan.ifconfig()[0]

# GIT Hub
github_user = "ulfmodig"
github_password = "LpQJdgB#s8&6AqD!"

# MQTT
mqtt_server = '192.168.1.90'

# GPIO
gpio_button_red = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_button_blue = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_button_yellow = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_button_green = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_button_white = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_button_black = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
gpio_led_red = machine.Pin(21, machine.Pin.OUT)
gpio_led_blue = machine.Pin(20, machine.Pin.OUT)
gpio_led_yellow = machine.Pin(19, machine.Pin.OUT)
gpio_led_green = machine.Pin(18, machine.Pin.OUT)

while wlan.isconnected() == False:
    pass
