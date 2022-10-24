from ast import match_case
import serial

start_byte = 0xFD
device_ıd = 0
command_ıd = 0
packet_no = 0
packet_size =0
payload = [1,8,2,17]


packet_state= start_byte
device_ıd= device_ıd
def data_process(value,start_byte):
    byte_array=[]
    global packet_state
    global packet_flag
    global n_flag
    global n_flag2

    match packet_state:

        case start_byte:
            byte_array.append(start_byte)
            packet_state = device_ıd

        case workk.device_ıd:
            device_ıd = i
            byte_array.append(device_ıd)
            packet_state = workk.command_ıd

        case workk.command_ıd:
            byte_array.append(workk.command_ıd) #arraye work.py deki command ıd değeri eklenmeyebilir.    
            packet_state = workk.packet_no # bu kısımda workteki değeri alması hatalı
        
        case workk.packet_no: 
            byte_array.append()
            packet_state = workk.packet_size

        case workk.packet_size:
            packet_size = workk.payload

        case workk.payload:
            byte_array = byte_array + workk.payload    
            

          
for i in range(15):
    print(device_ıd,"deviceID")
    data_process(i,packet_state)
    device_ıd += 1

