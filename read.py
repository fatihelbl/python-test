import argparse
from ctypes import sizeof
from multiprocessing.connection import wait
from time import sleep
from typing import Counter
import serial
import workk

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str,default=0)
parser.add_argument('--baudrate',type=str,default=0)
args = parser.parse_args()

ser = serial.Serial()
ser.baudrate = args.baudrate
ser.timeout = 5
ser.port = args.port
ser.open()

#port='COM9'
#ser=serial.Serial(port, baudrate=115200,timeout=5)

packet_state= workk.state_start_byte

def ACK_process(answer):
    byte_array=[]
    global packet_state
 
    match packet_state:

        case workk.state_start_byte:
            if answer[workk.state_start_byte] == workk.start_byte:
                packet_state = workk.state_checksum
                ACK_flag = 1

        case workk.state_checksum:
            checksum_index = len(answer)-1
            if ACK_flag and answer[checksum_index] == workk.crc16_generator(answer):
                print("crc")
                 
            

#@brief Parse incoming data to the function into Intel HEX format.
#@param line
#@return None  
def parse(line):
    
    count=1
    byte_count_value =line[count:count+2]    
    byte_count = int (byte_count_value, base=16)
    print("byte count",byte_count_value,"count", byte_count)
    count_data=byte_count
    count=count+2

    address= line[count:count+4]
    print("adress",address)
    count= count+4

    rec_type_ad= line[count:count+2]
    rec_type_count = int( line[count:count+2], base=16 )
    
    print("rec_type",rec_type_ad,"count",rec_type_count)
    rec_type=type_parser(rec_type_ad)

    if(rec_type=='data'):
        count=count+2
        data= line[count:(count+(count_data*2))]
        print("data",data)
        count=count+(count_data*2)
        checksum= line[count:count+2]
        checksum_count = int(line[count:count + 2], base=16)
        print("checksum", checksum, "checksum count", checksum_count)

        send_uart(data, address ,byte_count, checksum_count)

    if(rec_type == 'end'):
        count = count + 2
        print("Not data,End of file!")
        checksum= line[count:count + 2]
        checksum_count = int(line[count:count + 2],base = 16)
        print("checksum", checksum, "checksum count", checksum_count)

#@brief Sending data UART.
#@param data,address,byte_count
#@return None 
def send_uart(data,address,byte_count,checksum_count):
    bytess = []

    if(byte_count):
        bytess.append(byte_count)

    if(len(address) % 2 == 0):
        adr_lenght = int(len(address) / 2)
        
        for i in range(adr_lenght):
            bytess.append(int(address[i * 2 : (i * 2) + 2], base = 16))  
    
    if(len(data) % 2 == 0):
        str3_lenght = int(len(data) / 2)      
        
        for i in range(str3_lenght):
            bytess.append(int(data[i *2 : (i * 2) + 2], base = 16))                          
    
    if(checksum_count):
        bytess.append(checksum_count)
    
    print(bytess)
    ser.write(bytess)


#@brief Parses record type data in Intel HEX format.
#@param rec_type_ad
#@return data and end  
def type_parser(rec_type_ad):

    if(rec_type_ad == '00'):
        return 'data'
    
    if(rec_type_ad == '01'):
        return 'end'
 
#main
if( ser.in_waiting() == workk.BTL_LENGHT):
    read_btl = ser.read(workk.BTL_LENGHT)
    loop=0
    while(workk.loop >= loop):
        ACK_process(read_btl)
        loop += 1
    exit()
    
f=open('hex_file.hex', 'rb')
lines=f.readlines()
lines_count = len(lines)
print(lines_count, "len")
for line in lines:
   
    line = line.decode()
    print(line)
    parse(line)


""""
byte=f.read()
byte=byte.decode()
parse(byte)
"""

