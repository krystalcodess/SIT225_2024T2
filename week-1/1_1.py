import serial
import random
import time
from datetime import datetime

# Set baud rate, same speed as set in your Arduino sketch.
baud_rate = 9600

# Set serial port as suits your operating system
s = serial.Serial('/dev/tty.usbmodem1301', baud_rate, timeout=5)

def log(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

while True:  # Infinite loop, keep running
    # Generate a random integer between 1 and 5.
    data_send = random.randint(1, 5)

    # Write the generated integer to the serial port, encode it as UTF-8.
    s.write(bytes(str(data_send) + '\n', 'utf-8'))
    log(f"Send >>> {data_send}")

    # Read from the serial port until a valid number is received.
    response = s.readline().decode("utf-8").strip()
    if response.isdigit():
        wait_time = int(response)
        log(f"Received <<< {wait_time} (Waiting for {wait_time} seconds)")
        
        # Sleep for the received amount of seconds.
        time.sleep(wait_time)
        log("Sleeping done")


