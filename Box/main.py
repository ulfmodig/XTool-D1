def send_status():
    global mqtt_client, device_name
    topic = "home/xtool-d1/" + device_name + "/status"
    json = ujson.dumps({"zone": "home/xtool-d1", "device": device_name, "command": "status", "on": gpio_12_relay.value() == 1})    
    print("Publishing topic:%s message:%s" % (topic, json))
    mqtt_client.publish(topic, json)

def subscribe_to(topic):
    global mqtt_client
    print("Subscribing to topic: " + topic)
    mqtt_client.subscribe(topic)

def subscribe_callback(topic, msg):
    global keep_running
    print("Received topic:%s message:%s" % (topic, msg))
    try:
        json_doc = ujson.loads(msg)
    except:
        print("Bad JSON")
        return

    if not json_doc["device"] or json_doc["device"] != device_name:
        print("Ignored, correct device missing")        
    elif not "command" in json_doc:
        print("Ignored, no 'command'!")
    
    elif json_doc["command"] == "reboot":
        machine.reset()        
    elif json_doc["command"] == "refresh":
        pass
    elif json_doc["command"] == "stop":
        keep_running = False;
    elif not json_doc["on"]:
        print("Ignored, no 'on'!")    
    elif json_doc["command"] == "set_power" and json_doc["on"]:                
        gpio_12_relay.value(1)        
    elif json_doc["command"] == "set_power" and not json_doc["on"]:                
        gpio_12_relay.value(0)
        
    else:
        print("Ignored, unsupported command: " + json_doc["command"])
        
    send_status()


def connect_and_subscribe():
    global mqtt_client
    mqtt_client = MQTTClient(client_id=device_name, server=mqtt_server, user=mqtt_user, password=mqtt_password)    
    mqtt_client.connect()
    mqtt_client.set_callback(subscribe_callback)
    subscribe_to("home/xtool-d1/" + device_name + "/set")
    subscribe_to("home/xtool-d1/" + device_name + "/refresh")
    subscribe_to("home/xtool-d1/" + device_name + "/reboot")    

def restart_and_reconnect():
    print('Turning off...')
    gpio_12_relay.value(0)
    time.sleep(10)
    print('Rebooting...')    
    machine.reset()

devices = {'4cebd6acefc1': 'laser', '4cebd6ae22fd': 'air',
           '4cebd6ae2296': 'smoke', '4cebd6ae233d': 'enclosure',
           '4cebd6ae2201': 'test'}
device_name = devices[wlan_mac_address]
keep_running = True;
try:
    print("Starting up...")
    connect_and_subscribe()
    print("IP-Address...: " + wlan_ip_address)
    print("MAC-Address..: " + wlan_mac_address)
    print("MQTT-Broker..: " + mqtt_server)
    print("Device name..: " + device_name)
    send_status()
    print("Started!")
except:
    restart_and_reconnect()

counter = 0

while keep_running == True:
    try:

        # Check message and blink
        mqtt_client.check_msg()
        time.sleep(1)
        gpio_13_led.value(1) if gpio_13_led.value() == 0 else gpio_13_led.value(0)

        # Alive
        counter += 1
        if (counter > 60 * 30):
            send_status()
            counter = 0

    except:
        restart_and_reconnect()
