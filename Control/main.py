def send_command(topic, command):
    global mqtt_client, device_group, device_name, version
    json = ujson.dumps({"type": "xtool-D1", "device": device_name, "version": version, "command": command,"status": "on" if gpio_12_relay.value() == 0 else "off"})    
    print("Publishing topic:%s message:%s" % (topic, json))
    mqtt_client.publish(tpoic, json)

def subscribe_to(topic):
    global mqtt_client
    print("Subscribing to topic: " + topic)
    mqtt_client.subscribe(topic)

def subscribe_callback(topic, msg):
    print("Received topic:%s message:%s" % (topic, msg))
    try:
        json_doc = ujson.loads(msg)
    except:
        print("Bad JSON")
        return

    if not "type" in json_doc or not json_doc["type"] == "xtool-D1":
        pass
    elif not "status" in json_doc:
        pass
    else:
        if json_doc["device"] == "home/xtool-D1/laser":
            gpio_led_red.value(1) if json_doc["status"] == "on" else gpio_led_red.value(1)
        elif json_doc["device"] == "home/xtool-D1/air":
            gpio_led_blue.value(1) if json_doc["status"] == "on" else gpio_led_blue.value(1)
        elif json_doc["device"] == "home/xtool-D1/smoke":
            gpio_led_yellow.value(1) if json_doc["status"] == "on" else gpio_led_yellow.value(1)
        elif json_doc["device"] == "home/xtool-D1/enclosure":
            gpio_led_green.value(1) if json_doc["status"] == "on" else gpio_led_green.value(1)


def connect_and_subscribe():
    client = MQTTClient(device_name, mqtt_server)
    client.connect()
    client.set_callback(subscribe_callback)
    subscribe_to(client, device_name)
    subscribe_to(client, device_group)
    return client


def restart_and_reconnect():
    print('Reconnecting...')
    gpio_12_relay.value(0)
    send_command("status")
    time.sleep(10)
    machine.reset()


device_name = "home/xtool-D1/control"
device_group = 'home/xtool-D1'
version = "1.00"

try:
    print("Starting up...")
    mqtt_client = connect_and_subscribe()
    print("Version......: " + version)
    print("IP-Address...: " + wlan_ip_address)
    print("MAC-Address..: " + wlan_mac_address)
    print("MQTT-Broker..: " + mqtt_server)
    print("Device name..: " + device_name)
    send_command("booted")
    print("Started!")
except OSError as e:
    restart_and_reconnect()

counter = 0
while True:
    try:

        # Check message 
        mqtt_client.check_msg()
        
        # Check 'single' buttons
        if not gpio_button_red.value():
            if gpio_led_red.value():
               send_command("home/xtool-D1/laser", "switch:off")
            else
               send_command("home/xtool-D1/laser", "switch:on")
        if not gpio_button_blue.value():
            if gpio_led_blue.value():
               send_command("home/xtool-D1/air", "switch:off")
            else
               send_command("home/xtool-D1/air", "switch:on")
        if not gpio_button_yellow.value():
            if gpio_led_yellow.value():
               send_command("home/xtool-D1/smoke", "switch:off")
            else
               send_command("home/xtool-D1/smoke", "switch:on")
        if not gpio_button_green.value():
            if gpio_led_green.value():
               send_command("home/xtool-D1/enclosure", "switch:off")
            else
               send_command("home/xtool-D1/enclosure", "switch:on")
               
        # Check 'multi' buttons        
        if not gpio_button_white.value():
            send_command("home/xtool-D1", "switch:on")
        if not gpio_button_black.value():
            send_command("home/xtool-D1", "switch:off")

        # Alive
        counter += 1
        if (counter > 60 * 30):
            send_command("alive")
            counter = 0

    except OSError as e:
        restart_and_reconnect()
