# IoT Environmental Monitoring System

Simple IoT environmental monitoring project for the IDC / Internet of Things course at UPV.

The system reads temperature and humidity from a Grove temperature/humidity sensor connected to a Raspberry Pi Pico W. The Pico W connects to Wi-Fi and publishes the readings using MQTT. The data can then be collected with Telegraf, stored in InfluxDB, and visualized in Grafana.

## Architecture

```text
Sensor → Raspberry Pi Pico W → Wi-Fi → MQTT → Telegraf → InfluxDB → Grafana
```

## Hardware

- Raspberry Pi Pico W / Pico 2 W
- Grove temperature/humidity sensor
- Grove connector cable
- Breadboard
- Jumper wires
- Micro-USB cable

## Wiring

The Grove sensor pins are labeled:

```text
GND | NC | SIG | VCC
```

The wiring used:

| Sensor pin | Wire color | Pico pin |
|---|---|---|
| GND | Black | GND |
| NC | White | Not connected |
| SIG | Yellow | GP15 |
| VCC | Red | 3V3 / 3V3(OUT) |

Important: the sensor is powered from `3V3`, not `VBUS` or any 5V pin, because Pico GPIO pins are not 5V tolerant.

## Files

On the Pico, the MQTT library must be present:

```text
/
├── main.py
├── config.py
└── umqtt/
    └── simple.py
```

## Configuration

Create a local `config.py` file on the Pico using this template:

```python
WIFI_SSID = "your_wifi_name"
WIFI_PASSWORD = "your_wifi_password"

MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883

CLIENT_ID = "pico_environment_sensor"
TOPIC = b"idc/pico/environment"
```

## Main program

`main.py` connects to Wi-Fi, reads the sensor, connects to MQTT, and publishes readings every 5 seconds.

```python
import network
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


connect_wifi()
client = connect_mqtt()

while True:
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()

        message = '{{"temperature": {}, "humidity": {}}}'.format(
            temperature,
            humidity,
        )

        print("Publishing:", message)
        client.publish(TOPIC, message)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
```

## MQTT message format

The Pico publishes to:

```text
idc/pico/environment
```

Example payload:

```json
{
  "temperature": 24,
  "humidity": 48
}
```

## Backend plan

The intended backend pipeline is:

1. Telegraf subscribes to the MQTT topic.
2. Telegraf parses the JSON messages.
3. InfluxDB stores the measurements.
4. Grafana displays temperature and humidity over time.

## Troubleshooting

### Sensor read fails

Check that:

- `VCC` is connected to `3V3`
- `GND` is connected to `GND`
- `SIG` is connected to `GP15`
- `NC` is not connected
- the code uses `dht.DHT11(Pin(15))`

### Wi-Fi fails

Check that:

- the SSID and password are correct
- the network supports 2.4 GHz Wi-Fi
- the network does not require enterprise login

### MQTT import fails

If this error appears:

```text
ImportError: no module named 'umqtt'
```

then the Pico is missing the MQTT helper library. Add this file:

```text
/umqtt/simple.py
```

### MQTT connection fails

Check that:

- the MQTT broker is running
- the broker IP address is correct
- port `1883` is open
- the Pico and broker are on the same network
