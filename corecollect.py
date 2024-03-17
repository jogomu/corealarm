import os
import sys
import time
import struct
import threading
import simplepyble

last_timestamp = time.time_ns()
last_timestamp_lock = threading.Lock()

def to_fahrenheit(celsius):
    return celsius * 1.8 + 32

def parse_characteristic(contents):
    global last_timestamp
    parsed_data = struct.unpack('<BhhhBB', contents)
    flags = parsed_data[0]
    temp_is_fahrenheit = (flags >> 3) & 1
    core_temp = parsed_data[1]
    skin_temp = parsed_data[2]
    quality = parsed_data[4]

    quality = quality & 7
    qualities = ['Invalid','Poor','Fair','Good','Excellent','','','N/A']

    if core_temp==32767:
        core_temp = None
    else:
        core_temp = core_temp / 100
        if not temp_is_fahrenheit:
            core_temp = to_fahrenheit(core_temp)

    skin_temp = skin_temp / 100
    if not temp_is_fahrenheit:
        skin_temp = to_fahrenheit(skin_temp)

    timestamp = time.time_ns()
    #print(f'{os.getpid()} {threading.current_thread().native_id} update')
    with last_timestamp_lock:
        last_timestamp = timestamp
    return (timestamp, core_temp,qualities[quality],skin_temp)

def parse_and_print(contents):
    timestamp, core_temp, quality, skin_temp = parse_characteristic(contents)
    core_temp_str = str(core_temp) if core_temp else ''
    # end with , so that we can filter on (probably) complete lines only
    line = f'{timestamp},{core_temp_str},{quality},{skin_temp},'
    print(line)
    sys.stdout.flush()

if __name__ == "__main__":
    target_service_id = '00002100-5b1e-4347-b07c-97b514dae121'
    target_characteristic_id = '00002101-5b1e-4347-b07c-97b514dae121'

    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found",file=sys.stderr)
        sys.exit(-1)

    if len(adapters) > 1:
        # Query the user to pick an adapter
        print("Please select an adapter:",file=sys.stderr)
        for i, adapter in enumerate(adapters):
            print(f"{i}: {adapter.identifier()} [{adapter.address()}]",file=sys.stderr)

        choice = int(input("Enter choice: "))
    else:
        choice = 0
    adapter = adapters[choice]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]",file=sys.stderr)

    adapter.set_callback_on_scan_start(lambda: print("Scan started.",file=sys.stderr))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete.",file=sys.stderr))

    # three tries
    peripheral=None
    for _ in range(3):
        # Scan for 10 seconds
        adapter.scan_for(10000)
        peripherals = adapter.scan_get_results()
        #print("The following peripherals were found:",file=sys.stderr)
        for p in peripherals:
            connectable_str = "Connectable" if p.is_connectable() else "Non-Connectable"
            #print(f"{p.identifier()} [{p.address()}] - {connectable_str}",file=sys.stderr)
            #print(f'    Address Type: {p.address_type()}',file=sys.stderr)
            #print(f'    Tx Power: {p.tx_power()} dBm',file=sys.stderr)
            manufacturer_data = p.manufacturer_data()
            for manufacturer_id, value in manufacturer_data.items():
                #print(f"    Manufacturer ID: {manufacturer_id}",file=sys.stderr)
                #print(f"    Manufacturer data: {value} {len(value)}",file=sys.stderr)
                pass

            services = p.services()
            for service in services:
                #print(f"    Service UUID: {service.uuid()}",file=sys.stderr)
                #print(f"    Service data: {service.data()}",file=sys.stderr)
                if service.uuid()==target_service_id:
                    peripheral=p
        if peripheral:
            break
    if not peripheral:
        print("CORE was not found",file=sys.stderr)
        sys.exit(-1)

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]",file=sys.stderr)
    try:
        peripheral.connect()
    except:
        print('Could not connect',file=sys.stderr)
        sys.exit(-1)

    print("Successfully connected",file=sys.stderr)
    #peripheral.write_command(target_service_id, target_characteristic_id, b'\x01\x00')
    peripheral.notify(target_service_id, target_characteristic_id, parse_and_print)
    # sleep forever
    while True:
        time.sleep(30)
        now = time.time_ns()
        #print(f'{os.getpid()} {threading.current_thread().native_id} check')
        with last_timestamp_lock:
            diff = now - last_timestamp
        #print(f'{diff/1_000_000_000} since last timestamp',file=sys.stderr)
        if diff > 30_000_000_000:
            break
    print('No data received, exiting',file=sys.stderr)
    sys.exit(-1)
