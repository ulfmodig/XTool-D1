def send_command(topic, command):
    global mqtt_client, device_group, device_name, version
    json = ujson.dumps({"type": "xtool-D1", "device": device_name, "version": version, "command": command})    
    print("Publishing topic:%s message:%s" % (topic, json))
    mqtt_client.publish(topic, json)

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
        print("Ignored, bad type!")
    elif not "status" in json_doc:
        print("Ignored, no status found!")
    else:
        if json_doc["device"] == "home/xtool-D1/laser":
            gpio_led_red.value(1) if json_doc["status"] == "on" else gpio_led_red.value(0)
        elif json_doc["device"] == "home/xtool-D1/air":
            gpio_led_blue.value(1) if json_doc["status"] == "on" else gpio_led_blue.value(0)
        elif json_doc["device"] == "home/xtool-D1/smoke":
            gpio_led_yellow.value(1) if json_doc["status"] == "on" else gpio_led_yellow.value(0)
        elif json_doc["device"] == "home/xtool-D1/enclosure":
            gpio_led_green.value(1) if json_doc["status"] == "on" else gpio_led_green.value(0)

def button_pressed_callback(pin):
    if pin == gpio_button_red:
        send_command("home/xtool-D1/laser", "switch:off" if gpio_led_red.value() == 1 else "switch:on")
    elif pin == gpio_button_blue:
        send_command("home/xtool-D1/air", "switch:off" if gpio_led_blue.value() == 1 else "switch:on")
    elif pin == gpio_button_yellow:
        send_command("home/xtool-D1/smoke", "switch:off" if gpio_led_yellow.value() == 1 else "switch:on")
    elif pin == gpio_button_green:
        send_command("home/xtool-D1/enclosure", "switch:off" if gpio_led_green.value() == 1 else "switch:on")
    elif pin == gpio_button_white:
        send_command("home/xtool-D1", "switch:on")
    elif pin == gpio_button_black:
        send_command("home/xtool-D1", "switch:off")

def connect_and_subscribe():
    global mqtt_client
    mqtt_client = MQTTClient(client_id=device_name, server=mqtt_server, user=mqtt_user, password=mqtt_password)
    mqtt_client.connect()
    mqtt_client.set_callback(subscribe_callback)
    subscribe_to(device_name)
    subscribe_to(device_group)

def restart_and_reconnect():
    print('Reconnecting...')
    time.sleep(10)
    machine.reset()

device_name = "home/xtool-D1/control"
device_group = 'home/xtool-D1'
version = "1.00"

try:
    print("Starting up...")
    gpio_led_red.value(0)
    gpio_led_blue.value(0)
    gpio_led_yellow.value(0)
    gpio_led_green.value(0)
    
    gpio_button_red.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    gpio_button_blue.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    gpio_button_yellow.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    gpio_button_green.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    gpio_button_white.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    gpio_button_black.irq(trigger = machine.Pin.IRQ_RISING, handler=button_pressed_callback)
    
    connect_and_subscribe()
    
    print("Version......: " + version)
    print("IP-Address...: " + wlan_ip_address)
    print("MAC-Address..: " + wlan_mac_address)
    print("MQTT-Broker..: " + mqtt_server)
    print("Device name..: " + device_name)
    send_command(device_group, "booted")
    send_command(device_group, "?status")
       
    print("Started!")
except OSError as e:
    restart_and_reconnect()

while True:
    try:

        # Check message 
        mqtt_client.check_msg()
        
        # Slow down
        time.sleep_ms(1000) 
        
    except OSError as e:
        restart_and_reconnect()
