# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Updated by Julie Barrett for a project. The MIT license stands.

import alarm
import time
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_magtag.magtag import MagTag


magtag = MagTag()
count = 5
maxCount = 10
minCount =0
prevCount=5
swearStr = "Sporks to give: "
# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
### Feeds ###

# Setup a feed named 'status' for publishing to a feed
status_feed = secrets["aio_username"] + "/feeds/status"

# Setup a feed named 'mood' for subscribing to changes
mood_feed = secrets["aio_username"] + "/feeds/status"

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % status_feed)
    # Subscribe to all changes on the status.
    client.subscribe(status_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
    keep_alive = 60,
    #ping_interval=30,
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
# mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

magtag.add_text(
    text_position=(
        20,50,
        (magtag.graphics.display.height // 2) - 1,
        45
        ),

    #text_anchor_point=(0.1, 0.0),
    text_scale=2,
    text_wrap=20,

    text=(str(swearStr) + str(count)),


)
magtag.add_text(
    text_position=(
        20,120,
        (magtag.graphics.display.height // 2) - 1,

        ),


    text_scale=1,


    text="Reset        +           -         Empty",


)

while True:

    if magtag.peripherals.button_a_pressed:
        # prevCount=count
        # print(prevCount)
        count = 5
        # print(count)
        magtag.set_text(str(swearStr) + str(count))

        time.sleep(1)

    if magtag.peripherals.button_b_pressed:
        # prevCount=count
        # print(prevCount)
        count = count + 1
        # print(count)
        magtag.set_text(str(swearStr) + str(count))

        time.sleep(1)

    if magtag.peripherals.button_c_pressed:

        # prevCount=count
        # print(prevCount)
        count = count - 1
        # print(count)

        magtag.set_text(str(swearStr)+ str(count))

        time.sleep(1)
    if magtag.peripherals.button_d_pressed:

        # prevCount=count
        # print(prevCount)
        count = count = 0
        # print(count)

        magtag.set_text(str(swearStr) + str(count))

        time.sleep(1)


    if count < 0:
        magtag.set_text("Your bucket is empty!")

        # prevCount=count
        # print(prevCount)
        count = 0
        # print(count)
        magtag.set_text(str(swearStr)+ str(count))
        time.sleep(1)


    elif count > maxCount:
        magtag.set_text("Your bucket runneth over!")

        # prevCount=count
        # print(prevCount)
        count = count = 10
        # print(count)
        magtag.set_text(str(swearStr)+ str(count))
        time.sleep(1)

    if count != prevCount:
        mqtt_client.loop()
        # Send a new message
  
        print(str(count))
        print("Sending status value: %d..." % count)
        prevCount=count
        mqtt_client.publish(status_feed, count)
        #mqtt_client.loop(10) #blocks for 10 sec.
        time.sleep(15)
    if count == prevCount:
        mqtt_client.loop()
        # Send a new message
        print(str(count))
        print("Sending status value: %d..." % count)
        prevCount=count
        mqtt_client.publish(status_feed, count)
        #mqtt_client.loop(15) #blocks for 5 sec.
        time.sleep(15)
    



