import time
from paho.mqtt.client import Client

last_esp32_message_time = 0

def on_connect(client, userdata, flags, rc):
    client.subscribe("esp32/status")

def on_message(client, userdata, msg):
    global last_esp32_message_time
    if msg.topic == "esp32/status":
        last_esp32_message_time = time.time()

mqtt_client = Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)  # Change if using external broker
mqtt_client.loop_start()
