import serial
import csv
import time

# Set up the serial connection
arduino_port = '/dev/tty.usbmodem1301'  # Change this to match your Arduino's port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)

# Open a CSV file to write the data
csv_file = 'ultrasonic_data.csv'
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Distance (cm)'])

    try:
        while True:
            # Read data from Arduino
            data = ser.readline().decode('utf-8').strip()
            
            # Check if the data is valid
            if data:
                try:
                    distance = float(data)
                    timestamp = time.time()
                    
                    # Write data to CSV
                    writer.writerow([timestamp, distance])
                    print(f"Timestamp: {timestamp}, Distance: {distance} cm")
                    
                except ValueError:
                    print(f"Invalid data received: {data}")
            
            time.sleep(0.1)  # Adjust delay as needed
            
    except KeyboardInterrupt:
        print("Data collection stopped.")

    finally:
        ser.close()
        print(f"Data saved to {csv_file}")

