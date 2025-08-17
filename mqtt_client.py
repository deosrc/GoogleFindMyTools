from datetime import datetime
from enum import Enum
from paho.mqtt.enums import MQTTErrorCode, MQTTProtocolVersion
from random import randint
import json
import paho.mqtt.client as mqtt

from NovaApi.ExecuteAction.LocateTracker.decrypted_location import WrappedLocation

class ConnectionStatus(Enum):
    ERROR = -1
    DISCONNECTED = 0
    CONNECTED = 1

class MqttClient:

    TOPIC_TYPE_NAME = "name"
    TOPIC_TYPE_LOCATION = "location"
    TOPIC_TYPE_ERROR = "error"

    def __init__(self, host: str, username: str, password: str):
        self._host = host

        self._connection_status = ConnectionStatus.DISCONNECTED
        self._client_id = f'google-find-{randint(0, 65535)}'

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self._client_id,
            protocol=MQTTProtocolVersion.MQTTv5)
        self._client.username_pw_set(username, password)

    def send_update(self, canonic_id: str, device_name: str, location: WrappedLocation) -> None:
        self._ensure_connected()
        if self._connection_status != ConnectionStatus.CONNECTED:
            return

        # Publish device information
        self._client.publish(
            self._get_topic(canonic_id, MqttClient.TOPIC_TYPE_NAME),
            device_name)
        self._client.publish(
            self._get_topic(canonic_id, MqttClient.TOPIC_TYPE_LOCATION),
            json.dumps({
                "latitude": location.latitude,
                "longitude": location.longitude,
                "altitude": location.altitude,
                "time": datetime.fromtimestamp(location.time).strftime('%Y-%m-%d %H:%M:%S'),
                "mqtt_source": "google-find"
            }))

        # Publish Home Assistant discovery topic
        self._client.publish(
            f"homeassistant/device_tracker/googlefind/{canonic_id}/config",
            json.dumps({
                "unique_id": canonic_id,
                "name": device_name,
                "json_attributes_topic": self._get_topic(canonic_id, MqttClient.TOPIC_TYPE_LOCATION),
                "source_type": "bluetooth_le"
            }))

    def send_error_update(self, canonic_id, device_name, err) -> None:
        self._ensure_connected()
        if self._connection_status != ConnectionStatus.CONNECTED:
            return

        # Publish device information
        self._client.publish(
            self._get_topic(canonic_id, MqttClient.TOPIC_TYPE_NAME),
            device_name)
        self._client.publish(
            self._get_topic(canonic_id, MqttClient.TOPIC_TYPE_ERROR),
            err)

    def _ensure_connected(self):
        if self._connection_status == ConnectionStatus.CONNECTED:
            return

        result = self._client.connect(self._host)
        if result == MQTTErrorCode.MQTT_ERR_SUCCESS:
            self._connection_status = ConnectionStatus.CONNECTED
        else:
            self._connection_status == ConnectionStatus.ERROR

    def _get_topic(self, canonic_id: str, type: str) -> str:
        return f"google-find/{canonic_id}/location"