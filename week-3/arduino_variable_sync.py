"""
    Requirement: arduino_iot_cloud
    Install: pip install arduino-iot-cloud

    @Ahsan Habib
    School of IT, Deakin University, Australia.
"""

import sys
import traceback
import random
from arduino_iot_cloud import ArduinoCloudClient
import asyncio

DEVICE_ID = "1493c7e6-47e1-4441-a042-f66da6d25a90"
SECRET_KEY = "NxNEQQn#lyKFeR0hfl1aabm@W"


# Callback function on temperature change event.
# 
def on_temperature_changed(client, value):
    print(f"New temperature: {value}")


def main():
    print("main() function")

    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register with 'temperature' cloud variable
    # and listen on its value changes in 'on_temperature_changed'
    # callback function.
    # 
    client.register(
        "temperature", value=None, 
        on_write=on_temperature_changed)

    # start cloud client
    client.start()


if __name__ == "__main__":
    try:
        main()  # main function which runs in an internal infinite loop
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_type, file=print)