import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

WIFI_SSID = "Nico sin iFån"
WIFI_PASSWORD="12345678"

MQTT_BROKER = "172.20.10.2"
MQTT_PORT = 1883

CLIENT_ID = "pico_nicolai_sensor"
TOPIC = b"idc/pico/environment"

sensor = dht.DHT11(Pin(15))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    MQTT_BROKER,
    MQTT_PORT,
    CLIENT_ID,
    TOPIC,
)

sensor = dht.DHT11(Pin(15))


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 20
        while timeout > 0:
            if wlan.isconnected():
                break
            print("Waiting for Wi-Fi...")
            time.sleep(1)
            timeout -= 1

    if not wlan.isconnected():
        print("Wi-Fi connection failed")
        raise SystemExit

    print("Wi-Fi connected")
    print("Network config:", wlan.ifconfig())


def connect_mqtt():
    print("Connecting to MQTT broker...")
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT connected")
    return client


def read_sensor():
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()

    return temperature, humidity


def publish_sensor_data(client, temperature, humidity):
    message = '{{"temperature": {}, "humidity": {}}}'.format(
        temperature,
        humidity,
    )

    print("Publishing:", message)
    client.publish(TOPIC, message)


connect_wifi()
client = connect_mqtt()

while True:
    try:
        temperature, humidity = read_sensor()
        publish_sensor_data(client, temperature, humidity)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 15
        while timeout > 0:
            if wlan.isconnected():
                break
            print("Waiting for Wi-Fi...")
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("Wi-Fi connected")
        print("Network config:", wlan.ifconfig())
    else:
        print("Wi-Fi connection failed")
        raise SystemExit

def connect_mqtt():
    print("Connecting to MQTT broker...")
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT connected")
    return client

connect_wifi()
client = connect_mqtt()

while True:
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()

        message = '{{"temperature": {}, "humidity": {}}}'.format(
            temperature,
            humidity
        )

        print("Publishing:", message)
        client.publish(TOPIC, message)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
