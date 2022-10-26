from ast import match_case
import serial
import workk
port='COM9'
ser=serial.Serial(port, baudrate=115200,timeout=5)

packet_state= workk.state_start_byte

def ACK_process(answer):
    global packet_state
 
    match packet_state:

        case workk.state_start_byte:
            if answer[workk.state_start_byte] == workk.start_byte:
                packet_state = workk.state_checksum
  

        case workk.state_checksum:
            checksum_index = len(answer)-1

            if answer[checksum_index] == workk.ACK_CRC:
                ACK_state_flag = 1
            
            elif answer[checksum_index] == workk.RJT_CRC:
                RJT_state_flag = 1

            else:
                print("TMT")    
        case workk.state_output:
            if ACK_state_flag:
                print("ack")
            elif RJT_state_flag:
                print("rjt")    

           # if ACK_flag and answer[checksum_index] == workk.crc16_generator(answer):
            
                                       
#main         

if(ser.in_waiting() == workk.BTL_LENGHT):
    read_btl = ser.read(workk.BTL_LENGHT)
    loop=0
    while(workk.loop >= loop):
        ACK_process(read_btl)
        loop += 1
    exit()
    


    
