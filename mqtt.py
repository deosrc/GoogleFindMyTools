import os
from time import sleep
from NovaApi.ListDevices.nbe_list_devices import get_devices
from NovaApi.ExecuteAction.LocateTracker.location_request import get_location_data_for_device
from NovaApi.ExecuteAction.LocateTracker.decrypted_location import WrappedLocation
from mqtt_client import MqttClient


mqtt = MqttClient(
    os.environ["MQTT_HOST"],
    os.environ["MQTT_USERNAME"],
    os.environ["MQTT_PASSWORD"])

def update_device(device_name, canonic_id):
    print(f"Updating device {device_name}...")
    try:
        locations = get_location_data_for_device(canonic_id, device_name)

        if locations:
            latest_location = next(iter(sorted(iter(locations), key=lambda x: x.time, reverse=True)), None)

            print("Sending device update to MQTT...")
            mqtt.send_update(canonic_id, device_name, latest_location)
    except Exception as err:
        print(f"Error updating device: {err}")
        mqtt.send_error_update(canonic_id, device_name, err)

def update_mqtt():
    print("Refreshing device list...")

    devices = get_devices()
    print(f"Retrieved {len(devices)} devices")

    for device_name, canonic_id in devices:
        update_device(device_name, canonic_id)

    print("Device updates complete")


if __name__ == '__main__':
    print("Starting MQTT mode...")

    while True:
        update_mqtt()
        sleep(60)