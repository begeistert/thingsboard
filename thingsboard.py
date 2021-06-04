import json
from umqtt.simple import MQTTClient
from server import *


class ThingsboardMQTTClient(MQTTClient):
    """
    Define un cliente especial para la conexión al servidor de Thingsboard

    Metodos:
        publish_telemetry: Utilizado para publicar parametros de telemetría
        subscribe_rpc: Utilizado para suscribirse y recibir comandos RPC
    """

    def __init__(self, port=1883):
        """
        :param port: Define el puerto de conexión al Broker
        """
        client_id = '253f0d70-ac5c-11eb-b641-bb94f8adb61c'
        super().__init__(client_id, server, user=access_token, password='',
                         port=port, keepalive=120)
        self._topic_telemetry = 'v1/devices/me/telemetry'
        self._topic_rpc = 'v1/devices/me/rpc/request/+'
        self.topic_attributes = 'v1/devices/me/attributes'

    def publish_telemetry(self, msg):
        """
        Publica datos de telemetria al servidor
        :param msg: Mensaje a enviar
        :return:
        """
        msg = json.dumps(msg)
        self.publish(self._topic_telemetry, msg)

    def subscribe_rpc(self):
        """
        Suscribe al canal RPC
        :return:
        """
        self.subscribe(self._topic_rpc, qos=1)
