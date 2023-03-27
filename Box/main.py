#  mosquitto_pub -t "home/xtool-D1" -m '{"command": "update", "path": "https://raw.githubusercontent.com/ulfmodig/XTool-D1/master", "file": "test.txt"}'
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
    json = ujson.dumps({"type": "xtool-D1", "device": device_name, "version": version, "command": command,"status": "on" if gpio_12_relay.value() == 0 else "off"})    
    print("Publishing topic:%s message:%s" % (topic, json))
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
        pass
    elif not json_doc["type"] == "xtool-D1"
        pass
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


devices = {'4cebd6acefc1': 'home/xtool-D1/laser', '4cebd6ae22fd': 'home/xtool-D1/air',
           '4cebd6ae2296': 'home/xtool-D1/smoke', '4cebd6ae233d': 'home/xtool-D1/enclosure'}
device_name = devices[wlan_mac_address]
device_group = 'home/xtool-D1'
version = "1.03"

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
