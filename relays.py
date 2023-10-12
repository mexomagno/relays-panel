import paho.mqtt.client as mqtt
from gpiozero import LED
import os
from dotenv import dotenv_values

ENV = dotenv_values('.env')

# Raspi gpios, in order of panel outputs
pins = [2, 3, 4, 17, 18, 15, 14]
if "arm" not in os.uname().machine:
    print("NOT a raspberry. leds initialized as empty")
    pins = list()
leds = [LED(pin) for pin in pins]


TOPIC = "depavalpo/living/#"
STATE_TOPIC_SUFFIX = "state"

def set_value(led, value):
    if value.lower().strip() in ['1', 'on', 'true']:
        led.on()
    else:
        led.off()

def set_value_all(value):
    for led in leds:
        set_value(led, value)

def get_state_topic(topic):
    return os.path.join('/'.join(topic.split("/")[:-1]), STATE_TOPIC_SUFFIX)


def on_connect(client, userdata, flags, rc):
    if rc > 0:
        print(f"Some error code!: {rc} {client} {userdata} {flags}")
    else:
        print("Connected successfully")
        client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"{msg.topic} Message received: {msg.payload}")
    command = msg.topic.strip("/").split("/")[-3:]
    # parse
    [device_class, pin_index, action] = command
    print(f"debug: msg.topic {msg.topic}, msg.payload {msg.payload}, parsed command {command}")
    if device_class == "relays":
        # ALL
        if action.lower() == "set":
            print("Action SET")

            payload = msg.payload.decode('utf-8')
            if pin_index.lower() == "all":
                print("Actuating ALL outputs with ", payload)
                set_value_all(payload)
                client.publish(f'{msg.topic}/state', payload)
                return

            # By index
            pin_index = int(pin_index) - 1
            if pin_index not in range(len(leds)):
                print(f"{device_class}[{pin_index}] (index {pin_index + 1}) is not defined.")
                return

            print(f"debug: Will set led[{pin_index}] to {payload}")
            set_value(leds[pin_index], payload)
            # confirm
            # client.publish(get_state_topic(msg.topic), payload)
            client.publish(f'{msg.topic.rsplit("/"+action, 1)[0]}/state', payload)
        elif action == 'state':
            print('Outbound state msg. Ignoring')
        else:
            print(f"Unsupported action '{action}'")

    else:
        print(f"Unsupported device class '{device_class}'")

client = mqtt.Client("raspi")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=ENV.get('MOQUITTO_USER'), password=ENV.get('MOSQUITTO_PASS'))
client.connect('192.168.1.2')  # todo: get programmatically
client.loop_forever()
