import argparse
import serial
import constants
import crc

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str,default=0)
args = parser.parse_args()

ser = serial.Serial()
ser.baudrate = 1200
ser.timeout = 5
ser.port = args.port
ser.open()

#@brief Sending BTL Protocol with UART.
#@param device_id: device number, 
#       packet_size: total packet, 
#       hex_data: hex address and data, 
#       packet_no: indicates the number of the packet sent.
#@return None                 
def send_btl_protocol(device_id,packet_size,hex_data,packet_no):
    byte=[constants.btl_start_byte]
    crc_array =[]
   
    if device_id <=255:
        byte.append(constants.device_id_second)

    byte.append(device_id)
    byte.append(constants.command_id)
    byte.append(packet_no)
     
    if packet_size <=255:
        byte.append(constants.packet_size_second)
    
    byte.append(packet_size)
    byte= byte+ hex_data
    crc_array = crc.crc16_generator(byte)    
    byte = byte +crc_array
    ser.write(byte)
    
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
device_id = 1
hex_data = []   
f = open('hex_file.hex', 'rb')
lines = f.readlines()
lines_count = len(lines)
packet_no = 0
for line in lines :       
            line = line.decode()
            hex_data = parse(line)
            send_btl_protocol(device_id,lines_count,hex_data,packet_no)
            packet_no += 1  


