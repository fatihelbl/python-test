import argparse
import serial
import constants
import crc

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str,default=0)
args = parser.parse_args()

ser = serial.Serial()
ser.baudrate = 115200
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
        flag=0
        checksum_count = int(line[count:count + 2], base=16)
        return send_hex_data(flag,data, address ,byte_count, checksum_count)
    
    if(rec_type == 'end'):
        count = count + 2
        flag=1
        data=[0]
        checksum_count = int(line[count:count + 2],base = 16)
        return send_hex_data(flag,data,address ,byte_count, checksum_count)
    
    if(rec_type=='extend'):
        count=count+2
        data= line[count:(count+(count_data*2))]
        count=count+(count_data*2)
        flag=0
        checksum_count = int(line[count:count + 2], base = 16)
        return send_hex_data(flag,data, address ,byte_count, checksum_count)

#@brief Sending hex data BTL Protocol .
#@param data,address,byte_count
#@return None 
def send_hex_data(flag,data,address,byte_count,checksum_count):
    bytes_array = []
    bytes_array.append(byte_count)
    if(len(address) % 2 == 0):
        adr_lenght = int(len(address) / 2)

        for i in range(adr_lenght):
            bytes_array.append(int(address[i * 2 : (i * 2) + 2], base = 16)) 
    if(flag==0):
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
    
    if(record_type == '04'):
        return 'extend'  
     
def casetest(line_count_start,line_count_end):
    global packet_no
    print("ilk 1024")
    hex_packet = hex_data_all[line_count_start:line_count_end]
    hex_packet_size =len(hex_packet)
    print(hex_packet,"first packet")
    packet_no += 1
    print(packet_no,"packet no")
    send_btl_protocol(device_id,hex_packet_size,hex_packet,packet_no)
     
state=constants.first_packet
def case():
    global state
   
    match state:
        case constants.first_packet:  
            casetest(constants.data_start,constants.data_first_packet)
            if(packet_size_test>1):
                state= constants.second_packet
                print(state)
                
        case constants.second_packet:
            casetest(constants.data_first_packet,constants.data_second_packet) 
            if(packet_size_test>2):
                state= constants.third_packet
                print(state)
             
        case constants.third_packet:
            casetest(constants.data_second_packet,constants.data_third_packet)
            if(packet_size_test>2):
                state= constants.four_packet
                print(state)      
        case constants.four_packet:
            casetest(constants.data_third_packet,constants.data_four_packet)
            if(packet_size_test>2):
                
                print(state)     

#main
device_id = 1
hex_data_all = []
hex_data = [] 
f = open('hex_file.hex', 'rb')
lines = f.readlines()
lines_count = len(lines)
packet_no = 0
for line in lines :       
            line = line.decode()
            hex_data = parse(line)
            hex_data_all = hex_data_all + hex_data  
          
packet_size = len(hex_data_all)
packet_size_test = packet_size/1024              
print(packet_size,"packet_size_all")
print(packet_size_test,"packet_size_test")
#print(hex_data_all,"hex data")     
loop=0
while(loop<(packet_size_test)):
    case()
    loop +=1
