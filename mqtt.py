from NovaApi.ListDevices.nbe_list_devices import get_devices
from NovaApi.ExecuteAction.LocateTracker.location_request import get_location_data_for_device

def update_device(device_name, canonic_id):
    print(f"Updating device {device_name}...")
    locations = get_location_data_for_device(canonic_id, device_name)
    print(locations)

def update_mqtt():
    print("Refreshing device list...")

    devices = get_devices()
    print(f"Retrieved {len(devices)} devices")

    for device_name, canonic_id in devices:
        update_device(device_name, canonic_id)

    print("Device updates complete")


if __name__ == '__main__':
    print("Starting MQTT mode...")
    update_mqtt()