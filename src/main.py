import json
import time
import uasyncio
from ota import *
from settings import *
from senko import Senko
from hcsr04 import HCSR04
from machine import Pin, reset
from thingsboard import ThingsboardMQTTClient

__version__ = '0.0.1'
__author__ = 'Iván Montiel Cardona'

# Configuración del sensor HCSR04
sensor = HCSR04(trigger_pin=trigger, echo_pin=echo)

# Pre-configuraciones del sistema
current_level = 100
manual = False  # Se desactiva por defecto el modo manual
filling = False

# Configuración del relay para la bomba de Agua
water_pump = Pin(pump, Pin.OUT)

# gpio2_pin = 5
# gpio_state = {
#    gpio2_pin: False
# }
data = {
    "Level": (sensor.distance_cm() / 100)
}
attributes = {
    'full': False,
    'empty': False
}

OTA = Senko(
  user=git_user,
  repo=git_repo,
  branch=git_branch,
  working_dir=wdir,
  files=sysfiles
)


def on_message(topic, msg):
    global manual
    msg = json.loads(msg)
    method_name = msg['method']
    if method_name == 'setValue':
        client.publish(str(topic).replace('request', 'response'), json.dumps({'turn_on': msg['params']}), qos=1)
        client.publish('v1/devices/me/attributes', json.dumps({'turn_on': msg['params']}), qos=1)
        manual = msg['params']
    elif method_name == 'checkStatus':
        client.publish(str(topic).replace('request', 'response'), json.dumps(attributes), qos=1)
        client.publish('v1/devices/me/attributes', json.dumps(attributes), qos=1)


def connect_and_subscribe():
    global client
    client = ThingsboardMQTTClient()
    client.set_callback(on_message)
    client.connect()
    client.subscribe_rpc()
    # client.publish('v1/devices/me/attributes', get_gpio_status(), qos=1)
    print('Connected to begeistert.studio MQTT broker, subscribed to v1/devices/me/telemetry topic')
    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    reset()


def calculate_level():
    global client, current_level, attributes
    current_level = (((sensor.distance_cm() * 100) / container_height) - 100) * -1
    if current_level < secure_level:
        attributes['empty'] = True
        attributes['full'] = False
    elif current_level > almost_full:
        attributes['empty'] = False
        attributes['full'] = True
    client.publish('v1/devices/me/attributes', json.dumps(attributes))
    return current_level

# Definición de rutinas asincronas


async def telemetry():
    """
    Rutina asíncrona para la obtención y publicación de datos de telemetría
    :return:
    """
    global client
    while True:
        try:
            data['Level'] = calculate_level()
            client.publish_telemetry(data)
            await uasyncio.sleep(2)
        except OSError:
            restart_and_reconnect()


async def rpc():
    """
    Rutina asíncrona para la comprobación de comandos RPC
    :return:
    """
    global client
    while True:
        try:
            client.check_msg()
            await uasyncio.sleep(0.1)
        except OSError:
            restart_and_reconnect()


async def fill_container():
    """
    Rutina asíncrona para el control de llenado del contenedor de agua
    :return:
    """
    global current_level, attributes, manual, filling
    while True:
        if not manual:
            if attributes['empty']:
                water_pump.on()
                filling = True
            elif attributes['full']:
                water_pump.off()
                filling = False
        else:
            water_pump.on()
            filling = True
            print(current_level)
            print(manual)
            if current_level > almost_full:
                manual = False
                filling = False
        await uasyncio.sleep(2)


async def ota_service():
    global OTA
    while True:
        if OTA.update() and not filling:
            print('An update is available and it will be installed')
            print('The system will reboot now')
            print('Rebooting...')
            time.sleep(5)
            reset()
        await uasyncio.sleep(3600)


try:
    # Se inicia la conexión al broker
    client = connect_and_subscribe()
except OSError as e:
    # En caso de error se reiniciará el dispositivo
    restart_and_reconnect()

# Obtener contexto para iniciar rutinas asíncronas
event_loop = uasyncio.get_event_loop()

# Cración de tareas asíncronas
event_loop.create_task(telemetry())
event_loop.create_task(rpc())
event_loop.create_task(fill_container())

# Ejecución infinita
event_loop.run_forever()
