import argparse
from cgi import test
import enum
from pickle import TRUE
import time
import serial
import workk
import constanst
from enum import Enum
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

class test():

    def start_byte():
        return constanst.start_byte
    def ACK_start_byte():
        return constanst.ACK_start_byte
    def ACK_state_start_byte():
        return constanst.state_start_byte
    def ACK_command_ıd():
        return constanst.command_ıd
    def BTL_lenght_func():
        return workk.BTL_LENGHT

packet_state= constanst.state_start_byte

def ACK_process(answer):
    global packet_state
    global ACK_state_flag
    global RJT_state_flag
    match packet_state:

        case constanst.state_start_byte:
            if answer[constanst.state_start_byte] == constanst.start_byte:
                packet_state = constanst.state_checksum
  

        case constanst.state_checksum:
            checksum_index = len(answer)-1

            if answer[checksum_index] == constanst.ACK_CRC:
                ACK_state_flag = 1
            
            elif answer[checksum_index] == constanst.RJT_CRC:
                RJT_state_flag = 1

            else:
                print("TMT")    
        case constanst.state_output:
            if ACK_state_flag:
                print("ack")
            elif RJT_state_flag:
                print("rjt")    

           # if ACK_flag and answer[checksum_index] == workk.crc16_generator(answer):
                
def send_version(device_id,packet_size,hex_data,packet_no):
    byte=[constanst.start_byte ]
    crc =[]
    print(byte,"start")
    byte.append(device_id)
    print(byte,"device_id")
    byte.append(constanst.command_ıd)
    byte.append(packet_no)
    byte.append(packet_size)
    #byte= byte+ constanst.payload  # 1.8.2 17
    byte= byte+ hex_data
    #print(byte,"ack kısmı byte")
    #byte.append(packet_size)
    #print(byte,"packet SİZE")
    crc = constanst.crc16_generator(byte)        
    byte = byte +crc
    print(byte,"son")
    #!ser.write(byte)

def read_ack():  
    time.sleep(0.5)    
    if( ser.inWaiting() == constanst.BTL_LENGHT ):
        read_btl = ser.read(constanst.BTL_LENGHT)
        loop=0
        while(constanst.loop >= loop):
            ACK_process(read_btl)
            loop += 1
    exit()    

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
        return send_uart(data, address ,byte_count, checksum_count)
        
    if(rec_type == 'end'):
        count = count + 2
        print("Not data,End of file!")
        checksum= line[count:count + 2]
        checksum_count = int(line[count:count + 2],base = 16)
        print("checksum", checksum, "checksum count", checksum_count)
        return send_uart(address ,byte_count, checksum_count)

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
    #ser.write(bytess)
    return bytess

def create_packet(device_id,hex_data,packet_size):
    btl_packet=[]
    crc =[]
    btl_packet.append(constanst.start_byte)
    btl_packet.append(device_id)
    btl_packet.append(constanst.command_ıd)
    #packet no
    btl_packet.append(packet_size)
    btl_packet= btl_packet.extend(hex_data)  # 1.8.2 17
    crc = constanst.crc16_generator(btl_packet)        
    btl_packet = btl_packet +crc
    ser.write(btl_packet)

#@brief Parses record type data in Intel HEX format.
#@param rec_type_ad
#@return data and end  
def type_parser(rec_type_ad):

    if(rec_type_ad == '00'):
        return 'data'
    
    if(rec_type_ad == '01'):
        return 'end'
    
#main
hex_data =[]   
f=open('hex_file.hex', 'rb')
lines=f.readlines()
lines_count = len(lines)
print(lines_count,"lines_count")
packet_no=0
for line in lines :        
            line = line.decode()
            hex_data = parse(line)
            
            print(hex_data,"hex_data")
            send_version(1,lines_count,hex_data,packet_no)
            packet_no+=1  
            #create_packet(id,hex_data,lines_count)
          
"""""
for id in range(15):    
    send_version(id,lines_count,hex_data)
    read_ack()
    if ACK_state_flag:
        for line in lines :        
            line = line.decode()
            hex_data = parse(line)
            print(hex_data,"hex_data")
            create_packet(id,hex_data,lines_count)
"""""            


"""""
for line in lines:
   
    line = line.decode()
    print(line)
    parse(line)
"""""


""""
byte=f.read()
byte=byte.decode()
parse(byte)
"""

