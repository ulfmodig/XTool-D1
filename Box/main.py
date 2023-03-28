#  mosquitto_pub -t "home/xtool-D1" -m '{"command": "update", "path": "https://raw.githubusercontent.com/ulfmodig/XTool-D1/master", "file": "test.txt"}'
#  mosquitto_pub -t "home/xtool-D1/test" -h "192.168.1.90" -m '{\"type\": \"xtool-D1\", \"command\": \"reboot\"}'
def ota_update(path, filename):
    # Download
    full_url = path + "/" + filename
    print("Downloading: " + full_url)
    response = urequests.get(full_url)
    with open('update.bin', 'wb') as file:
        file.write(response.content)

    # Update
    print("Updating: " + filename)
    try:
        os.remove(filename)
    except:
        pass
    os.rename("update.bin", filename)
    send_command("updated")

    # Restart
    restart_and_reconnect()

def send_command(command):
    global mqtt_client, device_group, device_name, version
    json = ujson.dumps({"type": "xtool-D1", "device": device_name, "version": version, "command": command,"status": "on" if gpio_12_relay.value() == 1 else "off"})    
    print("Publishing topic:%s message:%s" % (device_group, json))
    mqtt_client.publish(device_group, json)

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

    if not "type" in json_doc:
        print("Ignored, no 'type'!")
    elif not json_doc["type"] == "xtool-D1":
        print("Ignored, bad type; " + json_doc["type"])
    elif not "command" in json_doc:
        print("Ignored, missing 'command'!")
    elif json_doc["command"] == "switch:on":
        gpio_12_relay.value(1)
        send_command("status")        
    elif json_doc["command"] == "switch:off":
        gpio_12_relay.value(0)
        send_command("status")        
    elif json_doc["command"] == "?status":
        send_command("status")
    elif json_doc["command"] == "reboot":
        machine.reset()
    elif json_doc["command"] == "update":
        ota_update(json_doc["path"], json_doc["file"])
    else:
        print("Ignored, unsupported command; " + json_doc["command"])        


def connect_and_subscribe():
    global mqtt_client
    mqtt_client = MQTTClient(device_name, mqtt_server)
    mqtt_client.connect()
    mqtt_client.set_callback(subscribe_callback)
    subscribe_to(device_name)
    subscribe_to(device_group)

def restart_and_reconnect():
    print('Reconnecting...')
    gpio_12_relay.value(0)
    send_command("status")
    time.sleep(10)
    machine.reset()


devices = {'4cebd6acefc1': 'home/xtool-D1/laser', '4cebd6ae22fd': 'home/xtool-D1/air',
           '4cebd6ae2296': 'home/xtool-D1/smoke', '4cebd6ae233d': 'home/xtool-D1/enclosure',
           '4cebd6ae2201': 'home/xtool-D1/test'}
device_name = devices[wlan_mac_address]
device_group = 'home/xtool-D1'
version = "1.04"

try:
    print("Starting up...")
    connect_and_subscribe()
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

        # Check message and blink
        mqtt_client.check_msg()
        time.sleep(1)
        gpio_13_led.value(1) if gpio_13_led.value() == 0 else gpio_13_led.value(0)

        # Alive
        counter += 1
        if (counter > 60 * 30):
            send_command("alive")
            counter = 0

    except OSError as e:
        restart_and_reconnect()
