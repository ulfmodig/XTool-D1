def send_command(device_name, on):
    global mqtt_client
    topic = "home/xtool-d1/"+device_name+"/set"
    zone = "home/xtool-d1"
    command = "set_power"
    
    json = ujson.dumps({"zone": "home/xtool-d1", "device": device_name, "command": "set_power", "on": on})    
    print("Publishing topic:%s message:%s" % (topic, json))
    mqtt_client.publish(topic, json)

def send_refresh():
    global mqtt_client
    topic = "home/xtool-d1/refresh"
    print("Publishing topic:%s" % (topic))
    mqtt_client.publish(topic, "")

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

    if not "command" in json_doc or not json_doc["command"] == "status":
        print("Ignored, command:'%s' !" % (json_doc["command"]))
    elif not "on" in json_doc:
        print("Ignored, no 'on' found!")
    else:
        print(json_doc["on"]);
        if json_doc["device"] == "laser":
            gpio_led_red.value(1) if json_doc["on"] == True else gpio_led_red.value(0)
        elif json_doc["device"] == "air":
            gpio_led_blue.value(1) if json_doc["on"] == True else gpio_led_blue.value(0)
        elif json_doc["device"] == "smoke":
            gpio_led_yellow.value(1) if json_doc["on"] == True else gpio_led_yellow.value(0)
        elif json_doc["device"] == "enclosure":
            gpio_led_green.value(1) if json_doc["on"] == True else gpio_led_green.value(0)

def button_pressed_callback(pin):
    global debounce_time, last_interrupt_time
    current_time = time.ticks_ms()
    
    if time.ticks_diff(current_time, last_interrupt_time) < debounce_time:
        pass
    elif pin == gpio_button_red:
        send_command("laser", gpio_led_red.value() == 0)
    elif pin == gpio_button_blue:
        send_command("air", gpio_led_blue.value() == 0)
    elif pin == gpio_button_yellow:
        send_command("smoke", gpio_led_yellow.value() == 0)
    elif pin == gpio_button_green:
        send_command("enclosure", gpio_led_green.value() == 0)
    elif pin == gpio_button_white:
        send_command("laser", True)
        send_command("air", True)
        send_command("smoke", True)
        send_command("enclosure", True)        
    elif pin == gpio_button_black:
        send_command("laser", False)
        send_command("air", False)
        send_command("smoke", False)
        send_command("enclosure", False)
        
    last_interrupt_time = current_time
        

def connect_and_subscribe():
    global mqtt_client
    mqtt_client = MQTTClient(client_id="xtool-d1", server=mqtt_server, user=mqtt_user, password=mqtt_password)
    mqtt_client.connect()
    mqtt_client.set_callback(subscribe_callback)
    subscribe_to("home/xtool-d1/laser/status")
    subscribe_to("home/xtool-d1/air/status")
    subscribe_to("home/xtool-d1/smoke/status")
    subscribe_to("home/xtool-d1/enclosure/status")    


def restart_and_reconnect():
    print('Reconnecting...')
    time.sleep(10)
    machine.reset()

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
    
    print("IP-Address...: " + wlan_ip_address)
    print("MAC-Address..: " + wlan_mac_address)
    print("MQTT-Broker..: " + mqtt_server)
       
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
