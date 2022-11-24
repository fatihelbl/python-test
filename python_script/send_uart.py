import serial

#@brief UART Configuration
port='COM8'
ser=serial.Serial(port, baudrate=115200,timeout=0)

#@brief File read operation and UART data transmission
#@param None
#@return None  
def read_file():
    file_name = input("Enter the file name.")
    f=open(file_name, 'rb')
    line =[]
    fileContents = f.read() 
    for b in fileContents:
        line.append(b)
    ser.write(line)
    line=[]

#@brief main function
#@param None
#@return None
def main():
    read_file()

main()
ser.close()