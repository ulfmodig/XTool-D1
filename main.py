def ota_update(path, file):

    # Download
    full_url = path + "/" + file
    print("Downloading: " + full_url)    
    response = urequests.get(full_url, auth=(github_user, github_password))
    with open('update.bin', 'wb') as file:
        file.write(response.content)
        
    # Update
    print("Updating: " + file)        
    if(os.path.isfile(file)):
        os.remove(file)
    os.rename("update.bin", file)
    
    # Restart
    restart_and_reconnect()        

def send_mqtt_message(client, topic, msg):
    json = ujson.dumps(msg)
    print("Publishing topic:%s message:%s" % (topic,json))
    client.publish(topic,json)
    
def subscribe_to(client, topic):
    print("Subscribing to topic: "+topic)
    client.subscribe(topic)
    
def subscribe_callback(topic, msg):
    print("Received topic:%s message:%s" % (topic, msg))
    json_doc = ujson.loads(msg)
    
    if not "command" in json_doc:
        pass
    elif json_doc["command"] == "switch:on":
        gpio_12_relay.value(1)
    elif json_doc["command"] == "switch:off":
        gpio_12_relay.value(0)
    elif json_doc["command"] == "?status":
        data = {"device": device_name, "status": "on" if gpio_12_relay.value() == 0 else "off"}       
        send_mqtt_message(device_group, data)
    elif json_doc["command"] == "reboot":
        machine.reset()
    elif json_doc["command"] == "update":
        ota_update(json_doc["path"], json_doc["file"])

def connect_and_subscribe():
    client = MQTTClient(device_name, mqtt_server)
    client.connect()
    client.set_callback(subscribe_callback)    
    subscribe_to(client,device_name)
    subscribe_to(client,device_group)    
    return client

def restart_and_reconnect():
    print('Reconnecting...')
    time.sleep(10)
    machine.reset()

devices = {'4cebd6acefc1': 'home/xtool-D1/laser','4cebd6ae22fd': 'home/xtool-D1/air','4cebd6ae2296': 'home/xtool-D1/smoke','4cebd6ae233d': 'home/xtool-D1/enclosure'}
device_name = devices[wlan_mac_address]
device_group = 'home/xtool-D1'
version = "1.01"

try:
    print("Starting up...")
    client = connect_and_subscribe()
    print("Version......: " + version)    
    print("IP-Address...: " + wlan_ip_address)
    print("MAC-Address..: " + wlan_mac_address)    
    print("MQTT-Broker..: " + mqtt_server)
    print("Device name..: " + device_name)
    data = {"device": device_name, "status": "booted"}       
    send_mqtt_message(client, device_group, data)      
    print("Started!")
except OSError as e:
    restart_and_reconnect()

counter=0
while True:
  try:
    
    # Check message and blink
    client.check_msg()
    time.sleep(1)
    gpio_13_led.value(1) if gpio_13_led.value() == 0 else gpio_13_led.value(0)
    
    # Alive
    counter += 1
    if(counter > 60*30):
        data = {"device": device_name, "status": "alive"}               
        send_mqtt_message(client, device_group, data)
        counter = 0
    
  except OSError as e:
    restart_and_reconnect()
