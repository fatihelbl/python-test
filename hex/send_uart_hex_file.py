import argparse
import serial
import constants
import crc
import time

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str,default=0)
args = parser.parse_args()

ser = serial.Serial()
ser.baudrate = 1200
ser.timeout = 5
ser.port = args.port
ser.open()

packet_state= constants.state_start_byte

def ACK_process(answer):
    global packet_state
    global ACK_state_flag
    global RJT_state_flag
    match packet_state:

        case constants.state_start_byte:
            if answer[constants.state_start_byte] == constants.start_byte:
                packet_state = constants.state_checksum
        case constants.state_checksum:
            checksum_index = len(answer)-1

            if answer[checksum_index] == constants.ACK_CRC:
                ACK_state_flag = 1
                packet_state = constants.state_output
            elif answer[checksum_index] == constants.RJT_CRC:
                RJT_state_flag = 1
                packet_state = constants.state_output
            else:
                print("TMT")    
        case constants.state_output:
            if ACK_state_flag:
                print("ack")
            elif RJT_state_flag:
                print("rjt")    

def send_version(device_id,packet_size,packet_no):
    byte=[constants.btl_start_byte ]
    crc_array =[] 
    print(byte,"start")
    byte.append(device_id)
    print(byte,"device_id")
    byte.append(constants.command_ıd)
    byte.append(packet_no)
    byte.append(packet_size)
    byte= byte+ constants.payload  # 1.8.2 17
    #byte= byte+ hex_data
    print(byte,"ack kısmı byte")
    #byte.append(packet_size)
    #print(byte,"packet SİZE")
    crc_array = crc.crc16_generator(byte)        
    byte = byte +crc_array
    print(byte,"son")
    ser.write(byte)                

def read_ack():  
    time.sleep(0.5)    
    if( ser.inWaiting() == constants.BTL_LENGHT ):
        read_btl = ser.read(constants.BTL_LENGHT)
        loop=0
        while(constants.loop >= loop):
            ACK_process(read_btl)
            loop += 1
         

    

#@brief Sending BTL Protocol with UART.
#@param device_id: device number, 
#       packet_size: total packet, 
#       hex_data: hex address and data, 
#       packet_no: indicates the number of the packet sent.
#@return None                 
def send_btl_protocol(device_id,packet_size,hex_data,packet_no):
    byte=[constants.btl_start_byte]
    crc_array =[]
    print(packet_size,"packet size")
    if packet_size > 255:
        hex_str = '{:04x}'.format(packet_size)
        print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        arr = [x, y]
        #arr = [hexstr[2:4],hexstr[4:6]]
        print(x,"x")
        print(y,"y")
        byte.append(x)
        byte.append(y)
    else :
        byte.append(packet_size)
    print(byte,"packet size add")
    #if device_id <=255:
    #    byte.append(constants.device_id_second)

    byte.append(device_id)
    byte.append(constants.command_id)
    byte.append(packet_no)
    print(byte,"device,command,packet no ")     
    #if packet_size <=255:
    #    byte.append(constants.packet_size_second)
    
    #byte.append(packet_size)
    byte= byte+ hex_data
    crc_array = crc.crc16_generator(byte)
    print(crc_array,"crc")    
    byte = byte +crc_array
    ser.write(byte)
    print(byte,"all protokol")
    
#@brief Parse incoming data to the function into Intel HEX format.
#@param line
#@return The send_hex_data function returns the address and data information of the hex.   
def parse(line):
    
    count=1
    byte_count_value =line[count:count+2]    
    byte_count = int (byte_count_value, base=16)
    count_data=byte_count
    count=count+2

    address= line[count:count+4]
    count= count+4
    
    record_type= line[count:count+2]
    rec_type=type_parser(record_type)

    if(rec_type=='data'):
        count=count+2
        data= line[count:(count+(count_data*2))]
        count=count+(count_data*2)
        checksum_count = int(line[count:count + 2], base=16)
        return send_hex_data(data, address ,byte_count, checksum_count)
    
    if(rec_type == 'end'):
        count = count + 2
        checksum_count = int(line[count:count + 2],base = 16)
        return send_hex_data(address ,byte_count, checksum_count)

#@brief Sending hex data BTL Protocol .
#@param data,address,byte_count
#@return None 
def send_hex_data(data,address,byte_count,checksum_count):
    bytes_array = []

    if(byte_count):
        bytes_array.append(byte_count)

    if(len(address) % 2 == 0):
        adr_lenght = int(len(address) / 2)
        
        for i in range(adr_lenght):
            bytes_array.append(int(address[i * 2 : (i * 2) + 2], base = 16))  
    print(address,"adress")
    if(len(data) % 2 == 0):
        data_lenght = int(len(data) / 2)      
        
        for i in range(data_lenght):
            bytes_array.append(int(data[i *2 : (i * 2) + 2], base = 16))                          
    
    if(checksum_count):
        bytes_array.append(checksum_count)
        
    return bytes_array


#@brief Parses record type data in Intel HEX format.
#@param rec_type_ad
#@return data and end  
def type_parser(record_type):

    if(record_type == '00'):
        return 'data'
    
    if(record_type == '01'):
        return 'end'
 
#main
hex_data_all = []
hex_data = []   
f = open('hex_file.hex', 'rb')
lines = f.readlines()
packet_no = 0
a=0
ACK_state_flag=0
for device_id in range(15):    
    
    if(device_id==5):
        send_version(device_id,a,packet_no)
        read_ack()
        ACK_state_flag=1    
    if (ACK_state_flag):
        for line in lines :       
            line = line.decode()
            hex_data = parse(line)
            hex_data_all = hex_data_all + hex_data  
            packet_no += 1
        lines_count = len(hex_data_all)              
        print(hex_data_all,"hex datası")
        send_btl_protocol(device_id,lines_count,hex_data_all,packet_no)
        ACK_state_flag=0
    
