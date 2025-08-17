import os
from time import sleep
from NovaApi.ListDevices.nbe_list_devices import get_devices
from NovaApi.ExecuteAction.LocateTracker.location_request import get_location_data_for_device
from NovaApi.ExecuteAction.LocateTracker.decrypted_location import WrappedLocation
from mqtt_client import MqttClient
from ProtoDecoders.decoder import DeviceInfo


mqtt = MqttClient(
    os.environ["MQTT_HOST"],
    os.environ["MQTT_USERNAME"],
    os.environ["MQTT_PASSWORD"])

update_interval=int(os.environ.get('UPDATE_INTERVAL', '120'))

def update_device(device_info: DeviceInfo):
    print(f"Updating device {device_info.name}...")
    try:
        locations = get_location_data_for_device(device_info.canonic_id, device_info.name)

        if locations:
            latest_location = next(iter(sorted(iter(locations), key=lambda x: x.time, reverse=True)), None)

            print("Sending device update to MQTT...")
            mqtt.send_update(device_info, latest_location)
    except Exception as err:
        print(f"Error updating device: {err}")
        mqtt.send_error_update(device_info, err)

def update_mqtt():
    print("Refreshing device list...")

    devices = get_devices()
    print(f"Retrieved {len(devices)} devices")

    for device_info in devices:
        update_device(device_info)

    print("Device updates complete")


if __name__ == '__main__':
    print("Starting MQTT mode...")

    while True:
        update_mqtt()
        sleep(update_interval)