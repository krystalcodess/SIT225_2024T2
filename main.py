
import serial
import csv
from datetime import datetime
import time

# Configure the serial port
SERIAL_PORT = '/dev/cu.usbmodem1201' 
BAUD_RATE = 9600
TIMEOUT = 1

# Configure the output CSV file
CSV_FILE = 'dht22_data.csv'

def read_serial_data(ser):
    """Read a line of data from the serial port."""
    line = ser.readline().decode('utf-8').strip()
    return line

def parse_data(line):
    """Parse the data line and extract humidity and temperature."""
    if "Humidity:" in line and "Temperature:" in line:
        parts = line.split('\t')
        humidity = float(parts[0].split(': ')[1].strip('%'))
        temperature = float(parts[1].split(': ')[1].strip('*C'))
        return humidity, temperature
    return None

def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser, \
             open(CSV_FILE, 'w', newline='') as csvfile:
            
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Timestamp', 'Humidity (%)', 'Temperature (°C)'])
            
            print(f"Logging data to {CSV_FILE}. Press Ctrl+C to stop.")
            
            while True:
                line = read_serial_data(ser)
                if line:
                    data = parse_data(line)
                    if data:
                        humidity, temperature = data
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        csv_writer.writerow([timestamp, humidity, temperature])
                        print(f"{timestamp}: Humidity: {humidity}%, Temperature: {temperature}°C")
                        csvfile.flush()  # Ensure data is written to file immediately
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print("Make sure your Arduino is connected and the correct port is specified.")

if __name__ == "__main__":
    main()