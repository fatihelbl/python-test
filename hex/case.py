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
ser.reset_input_buffer()
#@brief Sending BTL Protocol with UART.
#@param device_id: device number, 
#       packet_size: total packet, 
#       hex_data: hex address and data, 
#       packet_no: indicates the number of the packet sent.
#@return None                 
def send_btl_protocol(device_id,packet_size,hex_data,packet_no,command_id):
    byte=[constants.btl_start_byte]
    crc_array =[]
    print(packet_size,"packet size")
    if packet_size > 255:
        hex_str = '{:04x}'.format(packet_size)
        #print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        #print(x,"x")
        #print(y,"y")
        byte.append(x)
        byte.append(y)
    else :
        byte.append(constants.packet_size_second)
        byte.append(packet_size)
    print(byte,"packet size add")
    if device_id > 255:
        hex_str = '{:04x}'.format(device_id)
        #print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        #print(x,"x")
        #print(y,"y")
        byte.append(x)
        byte.append(y)
    else :
        byte.append(constants.packet_size_second)
        byte.append(device_id)
    print(byte,"device id add")
    byte.append(command_id)
    byte.append(packet_no)
    print(byte,"command,packet no ")     
    
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
    count=0
    two_dot_value = line[count:count+1]
    two_dot = ord(two_dot_value)
    count = count + 1

    byte_count_value =line[count:count+2]    
    byte_count = int (byte_count_value, base=16)
    count_data=byte_count
    count = count+2

    address= line[count:count+4]
    count = count + 4

    record_type= line[count:count+2]
    record_type_count = int (record_type, base=16)
    rec_type=type_parser(record_type)

    if(rec_type=='data'):
        count=count+2
        data= line[count:(count+(count_data*2))]
        count=count+(count_data*2)
        flag=0
        checksum_count = int(line[count:count + 2], base=16)
        return send_hex_data(flag,two_dot,byte_count,data, address ,record_type_count,checksum_count)
    
    if(rec_type == 'end'):
        count = count + 2
        flag=1
        data=[0]
        checksum_count = int(line[count:count + 2],base = 16)
        return send_hex_data(flag,two_dot,byte_count,data,address ,record_type_count,checksum_count)

#@brief Sending hex data BTL Protocol .
#@param data,address,byte_count
#@return None 
def send_hex_data(flag,two_dot,by_count,data,address,record_type,checksum):
    bytes_array = []
    # bytes_array.append(two_dot)
    # bytes_array.append(by_count)
    # bytes_array.append(record_type)
    # if(len(address) % 2 == 0):
    #     adr_lenght = int(len(address) / 2)

    #     for i in range(adr_lenght):
    #         bytes_array.append(int(address[i * 2 : (i * 2) + 2], base = 16)) 
    if(flag==0):
        if(len(data) % 2 == 0):
            data_lenght = int(len(data) / 2)      
        
            for i in range(data_lenght):
                bytes_array.append(int(data[i *2 : (i * 2) + 2], base = 16))                          
    # bytes_array.append(checksum)
    return bytes_array
def crc16_generator(data):
    data = bytearray(data)
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(0, 8):       
            bcarry = crc & 0x0001
            crc >>= 1
            if bcarry:
                crc ^= 0xa001

    if crc > 255:

        hex_str = '{:04x}'.format(crc)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        arr = [x, y]
        return arr
#@brief Parses record type data in Intel HEX format.
#@param rec_type_ad
#@return data and end  
def type_parser(record_type):

    if(record_type == '00'):
        return 'data'
    
    if(record_type == '01'):
        return 'end'
    
    if(record_type == '04'):
        return 'data'  

def reset_process():
    packet_state = constants.state_start_byte
    ACK_state_flag = 0
    RJT_state_flag = 0
    sequence_flag = 0
ACK_state_flag = 0
RJT_state_flag = 0
sequence_flag = 0    
packet_state= constants.state_start_byte
def answer_process(answer):
    
    print("case girdi")
    global packet_state
    global ACK_state_flag
    global RJT_state_flag
    global sequence_flag
    match packet_state:

        case constants.state_start_byte:
            if answer[constants.state_start_byte] == constants.ACK_start_byte:
                packet_state = constants.state_checksum
                sequence_flag=1

        case constants.state_checksum:

            if sequence_flag and crc16_generator(answer[0:4]) ==constants.ACK: #constants.ACK_CRC_SECOND:
                RJT_state_flag=0
                ACK_state_flag = 1
                packet_state = constants.state_output
                print("ACK cevabi geldi")
                
            elif sequence_flag and crc16_generator(answer[0:4]) ==constants.RJT_CRC:
                ACK_state_flag = 0
                RJT_state_flag = 1
                print("RJT cevabi geldi")
                packet_state = constants.state_output
            elif sequence_flag and crc16_generator(answer[0:4])== constants.TMT_CRC:
                ACK_state_flag = 0
                RJT_state_flag = 1
                print("TMT")    
        case constants.state_output:
            if ACK_state_flag:
                # print("ack")
                RJT_state_flag=0
                ACK_state_flag = 1
                packet_state= constants.state_start_byte
                #return 1
            elif RJT_state_flag:
                RJT_state_flag=1
                ACK_state_flag = 0
                # print("rjt")
                packet_state= constants.state_start_byte
                #return 2
                
def send_device_id(device_id,command_id,packet_no):
    byte=[constants.btl_start_byte ]
    crc_array =[] 
    print(byte,"start")
    if device_id > 255:
        hex_str = '{:04x}'.format(device_id)
        print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        # print(x,"x")
        # print(y,"y")
        byte.append(x)
        byte.append(y)
    else :
        byte.append(constants.device_id_second)
        byte.append(device_id)
    print(byte,"device_id")
    byte.append(command_id)
    byte.append(packet_no)
    byte.append(constants.device_id_command)
    byte.append(constants.device_id_command)
    crc_array = crc.crc16_generator(byte)        
    byte = byte +crc_array
    print(byte,"Devide id sorgulama")
    ser.write(byte)

def send_firmware(device_id,command_id,packet_no,packet_size_count):
    byte=[constants.btl_start_byte ]
    crc_array =[] 
    print(byte,"start")
    if device_id > 255:
        hex_str = '{:04x}'.format(device_id)
        print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        byte.append(x)
        byte.append(y)
    else :
        byte.append(constants.device_id_second)
        byte.append(device_id)
    print(byte,"device_id")
    byte.append(command_id)
    byte.append(packet_no)
    byte.append(constants.device_id_command)
    byte.append(constants.device_id_command)
    constants.payload.append(packet_size_count)
    print(constants.payload)
    byte= byte+ constants.payload  # 1.8.2 17
    payload_size = len(constants.payload)
    print(payload_size,"payload size")
    if payload_size > 255:
        hex_str = '{:04x}'.format(payload_size)
        #print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        #print(x,"x")
        #print(y,"y")
        byte.append(x)
        byte.append(y)
    else :
        byte.append(constants.packet_size_second)
        byte.append(payload_size)
    print(byte,"tüm packet SİZE")
    crc_array = crc.crc16_generator(byte)        
    byte = byte +crc_array
    print(byte,"firmware seri sorgulama")
    ser.write(byte)

def read_ack():  
    time.sleep(3)
    loop=1
    serial_waiting= ser.inWaiting()

    while(serial_waiting):
        serial_waiting=serial_waiting-1    
        read_btl = ser.read(constants.BTL_LENGHT)

        while(constants.loop >= loop):
            #state=answer_process(read_btl)
            answer_process(read_btl)
            loop +=1      
        serial_waiting=0
        loop=1 
        #return state                           
command_state= constants.state_command_id_4
def proces(device_id,packet_no):
    global command_state
    global sequence_flag
    rjt_count=0
    rjt_flag=1
    match command_state:

            case constants.state_command_id_4:
                send_device_id(device_id,constants.SEND_COMMAND_4,packet_no)
                print(device_id,".device sorgulamasi")
                read_ack()
                if(ACK_state_flag):
                    command_state = constants.state_command_id_3

            case constants.state_command_id_3:

                send_firmware(device_id,constants.SEND_COMMAND_3,packet_no,packet_size_count+1)
                ACK_state_flag=0
                print("firmware sorgulamasi")    
                read_ack()

                for_count=0
                packet_no = 1
                rjt_count=1
                for packet_sequence in range(packet_size_count+1):
                    rjt_flag=1
                    print(packet_size_count+1," adet paket var")
                    print(packet_sequence+1,".protokol paketi")
                    state= (packet_sequence+1) * 1024
                    hex_packet = hex_data_all[for_count : state ]
                    hex_packet_size = len(hex_packet)
                    for_count=state
                    if(ACK_state_flag):
                        send_btl_protocol(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_5) 
                        print(packet_no,".paket")
                        packet_no+=1
                        ACK_state_flag=0 

                    elif (RJT_state_flag):
                        while(rjt_count<3 and rjt_flag):
                            send_btl_protocol(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_5)       
                            print(packet_no,".paket")
                            read_ack()        
                            if(ACK_state_flag):
                                print(packet_no,".paket yollandır ACK alındı.")
                                packet_no+=1
                                ACK_state_flag=0
                                rjt_flag=0
                                break 
                            elif(rjt_count==2):
                                command_state =constants.state_command_id_51
                            rjt_count =rjt_count + 1    
                    
                    read_ack()
            case constants.state_command_id_51:
                if(retry_id==0):
                    send_firmware(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_51)
                    retry_id=1
                    command_state =constants.state_command_id_3 
                elif(retry_id==1):
                    send_firmware(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_51)
                    command_state= constants.state_command_id_4

#main
rety_id=0
device_id = 1
hex_data_all = []
hex_data = [] 
f = open('hex_file.hex', 'rb')
lines = f.readlines()
lines_count = len(lines)
packet_no = 1
for line in lines :       
            line = line.decode()
            hex_data = parse(line)
            hex_data_all = hex_data_all + hex_data  
          
packet_size = len(hex_data_all)
packet_size_count = int(packet_size/1024)              
print(packet_size,"tüm pakette yer alan veri sayisi")
print(packet_size_count+1," adet 1024' lük paket sayisi")
ACK_state_flag=0
device_id=0
command_state= constants.state_command_id_4
for i in range(3):
    device_id = i+1
    rjt_count=0
    rjt_flag=1
    match command_state:

            case constants.state_command_id_4:
                send_device_id(device_id,constants.SEND_COMMAND_4,packet_no)
                print(device_id,".device sorgulamasi")
                read_ack()
                print(ACK_state_flag,"ACK SORGU")
                if(ACK_state_flag):
                    command_state = constants.state_command_id_3

            case constants.state_command_id_3:

                send_firmware(device_id,constants.SEND_COMMAND_3,packet_no,packet_size_count+1)
                ACK_state_flag=0
                print("firmware sorgulamasi")    
                read_ack()

                for_count=0
                packet_no = 1
                rjt_count=1
                for packet_sequence in range(packet_size_count+1):
                    rjt_flag=1
                    print(packet_size_count+1," adet paket var")
                    print(packet_sequence+1,".protokol paketi")
                    state= (packet_sequence+1) * 1024
                    hex_packet = hex_data_all[for_count : state ]
                    hex_packet_size = len(hex_packet)
                    for_count=state
                    if(ACK_state_flag):
                        send_btl_protocol(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_5) 
                        print(packet_no,".paket")
                        packet_no+=1
                        ACK_state_flag=0 
                        command_state = constants.state_command_id_4

                    elif (RJT_state_flag):
                        while(rjt_count<3 and rjt_flag):
                            send_btl_protocol(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_5)       
                            print(packet_no,".paket")
                            read_ack()        
                            if(ACK_state_flag):
                                print(packet_no,".paket yollandır ACK alındı.")
                                packet_no+=1
                                ACK_state_flag=0
                                rjt_flag=0
                                break 
                            elif(rjt_count==2):
                                command_state =constants.state_command_id_51
                            rjt_count =rjt_count + 1    
                    
                    read_ack()
            case constants.state_command_id_51:
                if(retry_id==0):
                    send_firmware(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_51)
                    retry_id=1
                    command_state =constants.state_command_id_3 
                elif(retry_id==1):
                    send_firmware(device_id,hex_packet_size,hex_packet,packet_no,constants.SEND_COMMAND_51)
                    command_state= constants.state_command_id_4


        
