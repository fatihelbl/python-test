#@brief This function calculates the CRC-16 Modbus value of incoming data
#@param data : Data array sent from PC
#@return arr : crc converted to two one bytes.  
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