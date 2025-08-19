from datetime import datetime
from enum import Enum
from paho.mqtt.enums import MQTTErrorCode, MQTTProtocolVersion
from random import randint
import json
import paho.mqtt.client as mqtt
from ProtoDecoders.decoder import DeviceInfo

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

    def send_update(self, device_info: DeviceInfo, location: WrappedLocation) -> None:
        self._ensure_connected()
        if self._connection_status != ConnectionStatus.CONNECTED:
            return

        # Publish device information
        self._client.publish(
            self._get_topic(device_info.canonic_id, MqttClient.TOPIC_TYPE_NAME),
            device_info.name)
        self._client.publish(
            self._get_topic(device_info.canonic_id, MqttClient.TOPIC_TYPE_LOCATION),
            json.dumps({
                "latitude": location.latitude,
                "longitude": location.longitude,
                "altitude": location.altitude,
                "last_seen": datetime.fromtimestamp(location.time).strftime('%Y-%m-%d %H:%M:%S'),
                "mqtt_source": "google-find"
            }))

        # Publish Home Assistant discovery topic
        self._client.publish(
            f"homeassistant/device_tracker/googlefind/{device_info.canonic_id}/config",
            json.dumps({
                "unique_id": device_info.canonic_id,
                "json_attributes_topic": self._get_topic(device_info.canonic_id, MqttClient.TOPIC_TYPE_LOCATION),
                "source_type": "bluetooth_le",
                "device": {
                    "name": device_info.name,
                    "identifiers": [
                        device_info.canonic_id
                    ],
                    "manufacturer": device_info.manufacturer,
                    "model": device_info.model
                }
            }))

    def send_error_update(self, device_info: DeviceInfo, err) -> None:
        self._ensure_connected()
        if self._connection_status != ConnectionStatus.CONNECTED:
            return

        # Publish device information
        self._client.publish(
            self._get_topic(device_info.canonic_id, MqttClient.TOPIC_TYPE_NAME),
            device_info.name)
        self._client.publish(
            self._get_topic(device_info.canonic_id, MqttClient.TOPIC_TYPE_ERROR),
            str(err))

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