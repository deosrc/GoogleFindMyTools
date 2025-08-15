from NovaApi.ListDevices.nbe_list_devices import get_devices

def update_mqtt():
    print("Refreshing device list...")

    devices = get_devices()
    print(f"Retrieved {len(devices)} devices")

    for idx, (device_name, canonic_id) in enumerate(devices, start=1):
        print(f"{idx}: {device_name}")

if __name__ == '__main__':
    print("Starting MQTT mode...")
    update_mqtt()