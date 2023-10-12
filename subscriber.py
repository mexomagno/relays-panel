import paho.mqtt.client as mqtt
from gpiozero import LED
from dotenv import dotenv_values

ENV = dotenv_values('.env')

pins = [2, 3, 4, 17, 18, 15, 14]
leds = [LED(pin) for pin in pins]

topic = "/test/#"

def on_connect(client, userdata, flags, rc):
    if rc > 0:
        print(f"Some error code!: {rc}")
    else:
        print("Connected successfully")
        client.subscribe(topic)

relay1 = "/relay1"
relay2 = "/relay2"

def on_message(client, userdata, msg):
    print(f"{msg.topic} Message received: {msg.payload}")
    #print(f"Full msg: {msg}")
    # Get referenced relay

    relay_index = int(msg.topic.split('/')[-1][-1]) - 1
    led = leds[relay_index]
    print(f"actuating relay {relay_index + 1}")
    if msg.payload.decode('utf-8') in [1, "1", True, "true", "ON", "on"]:
        led.on()
    else:
        led.off()



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username="mosquitto", password=ENV.get('MOSQUITTO_PASS'))
#client.connect('homeassistant.local')
client.connect('192.168.1.83')
client.loop_forever()
