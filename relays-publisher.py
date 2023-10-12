import argparse
import paho.mqtt.client as mqtt
import os, time
from dotenv import dotenv_values

ENV = dotenv_values('.env')

def parse_args():
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('-r', '--relay', help="Relay index, 1-indexed")
  group.add_argument('-a', '--all', help="All relays", action="store_true")
  parser.add_argument('-v', '--value', help="On or Off")
  return parser.parse_args()

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

def connect():
  username=ENV.get('MOSQUITTO_USER')
  password=ENV.get('MOSQUITTO_PASS')
  host = ENV.get('MOSQUITTO_HOST')
  port = int(ENV.get('MOSQUITTO_PORT', 1883))
  print(f"Will connect as {username} with pass {password} to {host}:{port}")
  client = mqtt.Client()
  client.username_pw_set(username=username, password=password)
  # client.loop_start()
  client.on_connect = on_connect
  client.connect(host, port)
  client.loop_start()
  return client

CHANNEL = 'depavalpo/living/relays'
def send(client, relay_index, value):
  print(f"{relay_index} {value}")
  topic = os.path.join(CHANNEL, f"{relay_index}", "set")
  print(f"Sending payload '{value}' on topic '{topic}'")
  client.publish(topic, value)
  time.sleep(0.3)

def main():
  args = parse_args()
  print(f"args: {args}")
  # Try to connect to broker
  client = connect()
  # Send payload
  send(client, args.relay or (args.all and 'all'), args.value)
  # Report back

if __name__ == "__main__":
  main()

