import serial
import time

port='/dev/ttyACM0'
serial_arduino=serial.Serial(port,115200)

while True:
    cat_status=input('type: ');
    serial_arduino.write(cat_status.encode())
    input_s=serial_arduino.readline()
    print(input_s[:len(input_s)-1].decode())
