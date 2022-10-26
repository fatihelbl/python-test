import serial
import argparse
import constants
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str, default=0)
parser.add_argument('--frame', type=str, default=0)
parser.add_argument('--s', action='store_true')
parser.add_argument('--c', action='store_true')
parser.add_argument('--txt', type=str, default=0)
parser.add_argument('--command', type=str, default=0)
parser.add_argument('--pin', type=int, default=0)
parser.add_argument('--value', type=int, default=0)
args = parser.parse_args()

serial_comm = serial.Serial()
serial_comm.baudrate = 115200
serial_comm.port = args.port
serial_comm.open()

#@brief This functions send input value as 4 bytes
#@param value_package Input value
#@return void
def send_value(value_package):
    for i in value_package.to_bytes(4, byteorder='big'):
        serial_comm.write(constants.send_decimal(i))

#@brief This functions prints command by received command value
#@param commmand Received command value
#@return The name of value
def print_command(command):
    match command:
        case constants.COMMAND_INPUT_PIN:
            return "INPUT"
        case constants.COMMAND_ADC_PIN:
            return "ADC"

#@brief This functions clears the flags for new sequence
#@param void
#@return void
def reset_process():
    app_state = constants.STATE_START_BYTE
    handshake_flag = 0
    sequence_flag = 0
    exit()

#@brief This functions checks communication between pc and microcontroller are successfull
#@param void
#@return void
def check_connection():
    time.sleep(0.5)
    if(serial_comm.inWaiting() == constants.FAILED_CONNECTION):
        print("NCK: Check connection between PC and Microcontroller")
        exit()

handshake_flag = 0
sequence_flag = 0

app_state = constants.STATE_START_BYTE

#@brief This functions controls start byte and checksum byte is true and starts process
#@param Received answer from PIC
#@return void
def receive_process(answer):
    global app_state
    global handshake_flag
    global sequence_flag

    match app_state:
        case constants.STATE_START_BYTE:
            if answer[constants.STATE_START_BYTE] == constants.start_byte_sequence:
                app_state = constants.STATE_CHECKSUM
                sequence_flag = 1
            elif answer[constants.STATE_START_BYTE] == constants.start_byte_handshake:
                handshake_flag = 1
                app_state = constants.STATE_CHECKSUM
            else:
                print("NCK")

        case constants.STATE_CHECKSUM:
            checksum_index = len(answer)-1
            if sequence_flag and answer[checksum_index] == constants.sequence_checksum_calculator(answer):
                app_state = constants.STATE_OUTPUT
            elif handshake_flag and answer[constants.HANDSHAKE_CHECKSUM_INDEX] == constants.checksum_handshake:
                app_state = constants.STATE_OUTPUT
            else:
                print("NCK")

        case constants.STATE_OUTPUT:
            if sequence_flag:
                length = answer[constants.SEQ_LENGTH_INDEX]
                que = 0
                while(length):
                    print(print_command(answer[constants.SEQ_COMMAND_INDEX+(que * constants.SEQ_COMMAND_LENGTH)]), \
                                        answer[constants.SEQ_PIN_INDEX+(que * constants.SEQ_COMMAND_LENGTH)], \
                                        constants.cast_value(answer[constants.SEQ_VALUE1_INDEX+(que * constants.SEQ_COMMAND_LENGTH)], \
                                        answer[constants.SEQ_VALUE2_INDEX+(que * constants.SEQ_COMMAND_LENGTH)], \
                                        answer[constants.SEQ_VALUE3_INDEX+(que * constants.SEQ_COMMAND_LENGTH)], \
                                        answer[constants.SEQ_VALUE4_INDEX+(que * constants.SEQ_COMMAND_LENGTH)]))
                    que += 1
                    length -= 1
                reset_process()
            elif handshake_flag:
                print(chr(answer[constants.HANDSHAKE_VALUE1]), chr(answer[constants.HANDSHAKE_VALUE2]), chr(answer[constants.HANDSHAKE_VALUE3]))
                reset_process()
            else:
                print("NCK")

selected_pin = args.pin 
value = args.value
input_file = args.txt

sequence_frame = [0xBB, 0x0]

#MAIN
if(args.s):
    feedback_counter = 0
    line_counter = 0

    with open(sys.argv[constants.TXT_ARG_INDEX],'r') as file:
        for line in file:
            line_counter += 1

            if line.find("output") != -1:
                output_frame = [0x1, 0x0, 0x0, 0x0, 0x0, 0x0]
                data = line.split()
                output_frame[1] = int(data[1])
                output_frame[5] = int(data[2])
                sequence_frame.extend(output_frame)

            if line.find("input") != -1:
                feedback_counter += 1
                input_frame = [0x2, 0x0, 0x0, 0x0, 0x0, 0x0]
                data = line.split()
                input_frame[1] = int(data[1])
                sequence_frame.extend(input_frame)

            if line.find("adc") != -1:
                feedback_counter += 1
                adc_frame = [0x3, 0x0, 0x0, 0x0, 0x0, 0x0]
                data = line.split()
                adc_frame[1] = int(data[1])
                sequence_frame.extend(adc_frame)

            if line.find("dac") != -1:
                dac_frame = [0x4, 0x0]
                data = line.split()
                dac_frame[1] = int(data[1])
                extended_dac_frame = int(data[2]).to_bytes(4, byteorder='big')
                dac_frame.extend(extended_dac_frame)
                sequence_frame.extend(dac_frame)

            if line.find("delay") != -1:
                delay_frame = [0x6, 0x0]
                data = line.split()
                extended_delay_frame = int(data[1]).to_bytes(4, byteorder='big')
                delay_frame.extend(extended_delay_frame)
                sequence_frame.extend(delay_frame)

    file.close()

    sequence_frame[constants.SEQ_LENGTH_INDEX] = line_counter
    sequence_frame.append(constants.checksum_calculator(sequence_frame))

    total_length = (line_counter*6) + constants.CONTROL_PARAMETERS_LENGTH 
    
    i = 0
    while(i != total_length):
        serial_comm.write(constants.send_decimal(sequence_frame[i]))
        i += 1
    
    time.sleep(0.5)
    feedback_length = (feedback_counter * constants.SEQ_COMMAND_LENGTH) + constants.CONTROL_PARAMETERS_LENGTH 

    if serial_comm.inWaiting() == constants.HANDSHAKE_LENGTH:
        feedback = serial_comm.read(constants.HANDSHAKE_LENGTH)
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit()
    elif serial_comm.inWaiting() == feedback_length:
        feedback = serial_comm.read(feedback_length)
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit()
    else:
        print ("NCK")
        exit()
 
elif(args.c):
    if(args.command == 'output'): 
        serial_comm.write(constants.send_decimal(constants.start_byte_command))
        serial_comm.write(constants.send_decimal(constants.output_command))
        serial_comm.write(constants.send_decimal(selected_pin))
        send_value(value)
        checksum = (constants.sum_value(value) + constants.output_command + selected_pin) % constants.start_byte_command
        serial_comm.write(constants.send_decimal(checksum))
        check_connection()
        feedback = serial_comm.read(constants.HANDSHAKE_LENGTH)
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit()
                
    elif(args.command == 'input'): 
        serial_comm.write(constants.send_decimal(constants.start_byte_command))
        serial_comm.write(constants.send_decimal(constants.input_command))
        serial_comm.write(constants.send_decimal(selected_pin))
        send_value(constants.input_value)
        checksum = (constants.sum_value(constants.input_value) + constants.input_command + selected_pin) % constants.start_byte_command
        serial_comm.write(constants.send_decimal(checksum))
        check_connection()
        feedback = serial_comm.read(constants.COMMAND_FEEDBACK_LENGTH)
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit() 

    elif(args.command == 'adc'):
        serial_comm.write(constants.send_decimal(constants.start_byte_command))
        serial_comm.write(constants.send_decimal(constants.adc_command))
        serial_comm.write(constants.send_decimal(selected_pin))
        send_value(constants.adc_value)

        checksum = (constants.sum_value(constants.adc_value) + constants.adc_command + selected_pin) % constants.start_byte_command
        serial_comm.write(constants.send_decimal(checksum))
        check_connection()
        feedback = serial_comm.read(constants.COMMAND_FEEDBACK_LENGTH)
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit() 

    elif(args.command == 'dac'):
        serial_comm.write(constants.send_decimal(constants.start_byte_command))
        serial_comm.write(constants.send_decimal(constants.dac_command))
        
        if(constants.DAC_PIN == selected_pin):
            serial_comm.write(constants.send_decimal(selected_pin))
        else: 
            print("Invalid Pin value. Only pin 4 can set as DAC")
            reset_process()

        if((constants.MAX_DAC_VALUE > value) and (constants.MIN_DAC_VALUE <= value)):
            send_value(value)
        else: 
            print("Invalid value. Value must be between 0 and 31 for DAC")
            reset_process()

        checksum = (constants.sum_value(value) + constants.dac_command + selected_pin) % constants.start_byte_command
        serial_comm.write(constants.send_decimal(checksum))
        check_connection()
        feedback = serial_comm.read(constants.HANDSHAKE_LENGTH)
        
        loop = 0
        while(constants.FSM_LOOP >= loop):
            receive_process(feedback)
            loop += 1
        exit() 

    else:
        print("NCK")
else:
    print("NCK")


#python hwtf.py --port COM11 --s --txt delaytest.txt
#python hwtf.py --port COM11 --c --command output --pin 15 --value 1
#python hwtf.py --port COM11 --c --command input --pin 3 
#python hwtf.py --port COM11 --c --command adc --pin 3 
#python hwtf.py --port COM11 --c --command dac --pin 4 --value 20
