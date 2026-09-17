from wifi_packet import ESP32Server
from machine import Pin
import time

RELAY_PIN = 26
ILS_PIN = 27

door_sensor = Pin(ILS_PIN, Pin.IN, Pin.PULL_UP)
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)


def set_relay(value, door_status):
    if relay.value() == value:
        return

    relay.value(value)
    esp32.door_status = door_status


def is_door_closed():
    return door_sensor.value() == 0


def open_door():
    set_relay(0, "OPEN")
    print("Porte déverrouillée")


def close_door():
    if not is_door_closed():
        print("Fermeture refusée : la porte est encore ouverte")
        return

    set_relay(1, "CLOSED")
    print("Porte verrouillée")


def show_status():
    print("Statut de la porte :", "fermée" if is_door_closed() else "ouverte")


def respond_to_ping():
    print("Ping reçu")


COMMAND_HANDLERS = {
    b"OPEN": open_door,
    b"CLOSE": close_door,
    b"STATUS": show_status,
    b"PING": respond_to_ping,
}


def handle_command(command):
    handler = COMMAND_HANDLERS.get(command)

    if handler is not None:
        handler()


esp32 = ESP32Server(command_handler=handle_command)

try:
    esp32.wifi_connect("SSID", "ID", "PWD")
    esp32.start_server()
finally:
    esp32.server_stop()
    esp32.wifi_disconnect()


