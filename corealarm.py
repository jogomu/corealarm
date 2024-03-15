import struct
import simplepyble

# https://github.com/CoreBodyTemp/CoreBodyTemp/blob/main/CoreTemp%20BLE%20Service%20Specification.pdf

# TODO:
# - receive a continuously updated stream (and write to file for later charting)
# - alarm (continuously, loudly) on out of range or broken stream

# sample invocation/output:
#jmuehlhausen@CQ-JGM-MBP corealarm % python corealarm.py
#Selected adapter: Default Adapter [39a76676-2788-46c9-afa0-f0c0c31e6fd9] [39a76676-2788-46c9-afa0-f0c0c31e6fd9]
#Scan started.
#Scan complete.
#The following peripherals were found:
#CORE FA:B5 [59C16201-42D2-D4F0-932E-9A813D2801B7] - Connectable
#    Address Type: BluetoothAddressType.UNSPECIFIED
#    Tx Power: -32768 dBm
#    Manufacturer ID: 3062
#    Manufacturer data: b'\x00\x04u\x8e'
#    Service UUID: 00001809-0000-1000-8000-00805f9b34fb
#    Service data: b''
#    Service UUID: 0000180a-0000-1000-8000-00805f9b34fb
#    Service data: b''
#    Service UUID: 0000180f-0000-1000-8000-00805f9b34fb
#    Service data: b''
#    Service UUID: 00002100-5b1e-4347-b07c-97b514dae121
#    Service data: b''
#Connecting to: CORE FA:B5 [59C16201-42D2-D4F0-932E-9A813D2801B7]
#Successfully connected, listing services...
#Service: 00002100-5b1e-4347-b07c-97b514dae121
#    Characteristic: 00002101-5b1e-4347-b07c-97b514dae121
#        Contents: b'\x17@\x0e\xc1\r`\x08\x14\x00' (9)
#        skin: 1, core: 1, quality: 1, F: 0, heart rate: 1
#        3648 3521 2144 20 0
#        Core body temp: 97.664
#        Skin temp: 95.378

target_service_id = '00002100-5b1e-4347-b07c-97b514dae121'
target_characteristic_id = '00002101-5b1e-4347-b07c-97b514dae121'

if __name__ == "__main__":
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    if len(adapters) > 1:
        # Query the user to pick an adapter
        print("Please select an adapter:")
        for i, adapter in enumerate(adapters):
            print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

        choice = int(input("Enter choice: "))
    else:
        choice = 0
    adapter = adapters[choice]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    #adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

    # Scan for 10 seconds
    adapter.scan_for(10000)

    peripherals = adapter.scan_get_results()
    print("The following peripherals were found:")
    for peripheral in peripherals:
        services = peripheral.services()
        have_target=False
        for service in services:
            if service.uuid()==target_service_id:
                have_target=True
        if not have_target:
            continue


        connectable_str = "Connectable" if peripheral.is_connectable() else "Non-Connectable"
        print(f"{peripheral.identifier()} [{peripheral.address()}] - {connectable_str}")
        print(f'    Address Type: {peripheral.address_type()}')
        print(f'    Tx Power: {peripheral.tx_power()} dBm')

        manufacturer_data = peripheral.manufacturer_data()
        for manufacturer_id, value in manufacturer_data.items():
            print(f"    Manufacturer ID: {manufacturer_id}")
            print(f"    Manufacturer data: {value}")

        services = peripheral.services()
        for service in services:
            print(f"    Service UUID: {service.uuid()}")
            print(f"    Service data: {service.data()}")

        print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
        peripheral.connect()

        print("Successfully connected, listing services...")
        services = peripheral.services()
        for service in services:
            if service.uuid()!=target_service_id:
                continue
            print(f"Service: {service.uuid()}")
            for characteristic in service.characteristics():
                if characteristic.uuid() != target_characteristic_id:
                    continue
                print(f"    Characteristic: {characteristic.uuid()}")
                contents = peripheral.read(service.uuid(), characteristic.uuid())
                print(f"        Contents: {contents} ({len(contents)})")
                parsed_data = struct.unpack('<BhhhBB', contents)
                flags = parsed_data[0]
                skin_temp_present = (flags >> 0) & 1
                core_temp_present = (flags >> 1) & 1 # I think
                quality_present = (flags >> 2) & 1
                temp_is_fahrenheit = (flags >> 3) & 1
                heart_rate_present = (flags >> 4) & 1
                print(f'        skin: {skin_temp_present}, core: {core_temp_present}, quality: {quality_present}, F: {temp_is_fahrenheit}, heart rate: {heart_rate_present}')
                core_temp = parsed_data[1]
                skin_temp = parsed_data[2]
                reserved = parsed_data[3]
                quality = parsed_data[4]
                heart_rate = parsed_data[5]
                print(f'        {core_temp} {skin_temp} {reserved} {quality} {heart_rate}')
                
                core_temp = core_temp / 100
                if not temp_is_fahrenheit:
                    core_temp = (core_temp * 1.8) + 32
                print(f'        Core body temp: {core_temp}')

                skin_temp = skin_temp / 100
                if not temp_is_fahrenheit:
                    skin_temp = (skin_temp * 1.8) + 32
                print(f'        Skin temp: {skin_temp}')


        peripheral.disconnect()
