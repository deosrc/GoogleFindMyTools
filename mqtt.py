import os
from time import sleep
from NovaApi.ListDevices.nbe_list_devices import get_devices
from NovaApi.ExecuteAction.LocateTracker.location_request import get_location_data_for_device
from NovaApi.ExecuteAction.LocateTracker.decrypted_location import WrappedLocation
from mqtt_client import MqttClient
from ProtoDecoders.decoder import DeviceInfo
import logging


logging.basicConfig()

_LOGGER = logging.getLogger(__name__)

mqtt = MqttClient(
    os.environ["MQTT_HOST"],
    os.environ["MQTT_USERNAME"],
    os.environ["MQTT_PASSWORD"])

update_interval=int(os.environ.get('UPDATE_INTERVAL', '120'))

def update_device(device_info: DeviceInfo):
    _LOGGER.info("Updating device '%s'...", device_info.name)
    try:
        locations = get_location_data_for_device(device_info.canonic_id, device_info.name)

        if locations:
            latest_location = next(iter(sorted(iter(locations), key=lambda x: x.time, reverse=True)), None)

            _LOGGER.info("Sending '%s' device update to MQTT...", device_info.name)
            mqtt.send_update(device_info, latest_location)
    except Exception as err:
        _LOGGER.error(f"Error updating device.", exc_info=err)
        mqtt.send_error_update(device_info, err)

def update_mqtt():
    _LOGGER.info("Refreshing device list...")

    devices = get_devices()
    _LOGGER.info("Retrieved %i devices", len(devices))

    for device_info in devices:
        update_device(device_info)

    _LOGGER.info("Device updates complete")


if __name__ == '__main__':
    _LOGGER.info("Starting MQTT mode...")

    while True:
        update_mqtt()
        sleep(update_interval)
