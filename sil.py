import workk
import serial
port='COM9'
ser=serial.Serial(port, baudrate=115200,timeout=5)
array = [1,2,3]
arr = [4,5]
array = array + arr
#print(array)
test= workk.state_start_byte
match test:

    case workk.state_start_byte:
        print("oldu")
        array = array + workk.payload
        print(array)
        
      