import constants
import serial
import argparse
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

arr = []
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
        print(crc,"crcc")
        hex_str = '{:04x}'.format(crc)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        arr = [x, y]
        return arr
def reset_process():
    packet_state = constants.state_start_byte
    ACK_state_flag = 0
    RJT_state_flag = 0
    sequence_flag = 0
    exit()  
packet_state= constants.state_start_byte      
def ACK_process(answer):
    global packet_state
    global ACK_state_flag
    global RJT_state_flag
    global sequance_flag
    match packet_state:

        case constants.state_start_byte:
            if answer[constants.state_start_byte] == constants.ACK_start_byte:
                packet_state = constants.state_checksum
                sequance_flag=1
        case constants.state_checksum:
            checksum_index_first = len(answer)-2
            checksum_index_second = len(answer)-1
            if sequance_flag and crc16_generator(answer[0:4]) ==constants.ACK: #constants.ACK_CRC_SECOND:
                ACK_state_flag = 1
                packet_state = constants.state_output
                print("geldiack")
            elif sequance_flag and crc16_generator(answer[0:4]) ==constants.RJT_CRC:
                ACK_state_flag = 0
                RJT_state_flag = 1
                print("RJT")
                packet_state = constants.state_output
            else:
                print("TMT")    
        case constants.state_output:
            if ACK_state_flag:
                print("ack")
                reset_process()
            elif RJT_state_flag:
                print("rjt")   
                reset_process()

time.sleep(3)
serial_waiting= ser.inWaiting()
while(serial_waiting):
    serial_waiting= 0       
    read_btl = ser.read(constants.BTL_LENGHT)
    print(read_btl[4:])
    loop=0
    while(constants.loop >= loop):
        ACK_process(read_btl)
        loop += 1      
    